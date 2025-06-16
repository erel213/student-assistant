from abc import ABC, abstractmethod
import os
from src.llm_processor import Summary
from langchain.prompts import PromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AnyMessage
from enum import Enum
from typing import Annotated, Dict, Literal, Type, TypedDict, List, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.stdio import stdio_client
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import StateGraph, START, add_messages, MessagesState, END
from langgraph.graph.message import add_messages
from langgraph.types import Command
import logging
import json

class Exporter(ABC):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    @abstractmethod
    async def export(self, summary: Summary) -> None:
        pass

class MarkdownExporter(Exporter):
    def __init__(self, llm: BaseChatModel, export_path: str = None):
        if export_path is None:
            export_path = "summary.md"
        super().__init__(llm)
        self.export_path = export_path

    async def export(self, summary: Summary) -> None:
        formatted_summary = self._format_summary(summary)
        print(f"formatted_summary: {formatted_summary}")
        with open(self.export_path, "w") as f:
            f.write(formatted_summary)

    def _format_summary(self, summary: Summary) -> str:
        prompt = """
        you are expert in markdown formatting.
        you are given a summary of a presentation.
        you need to format the summary in markdown format.

        Here is the summary:
        {summary}

        Guidelines:
        1. Add Headers to the summary.
        2. Add subheaders to the summary.
        3. Add Table of Contents to the summary.
        4. use markdown formatting to format the summary.
        5. Use LaTeX to format mathematical expressions.
        a. Use $...$ for inline math.
        b. Use $$...$$ for display math.
        6. Use mermaid to format diagrams if you think it is useful to explain the concept.
        7. Use callouts to highlight important concepts ideas key terms and examples.
        8. Use bold to highlight important concepts ideas key terms and examples.
        9. Use italic to highlight important concepts ideas key terms and examples.
        10. Use underline to highlight important concepts ideas key terms and examples.
        11. Use strikethrough to highlight important concepts ideas key terms and examples.
        12. Use code to highlight important concepts ideas key terms and examples.
        13. Use code block to highlight important concepts ideas key terms and examples.
        14. Use code block to highlight important concepts ideas key terms and examples.
        """

        parser = StrOutputParser()
        chain = PromptTemplate.from_template(prompt) | self.llm | parser
        return chain.invoke({"summary": summary})


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    page_id: str
    summary: Summary
    block_ids: List[str]
    verification_results: Dict[str, bool]
    remaining_steps: int


class NotionMcpExporter(Exporter):
    def __init__(self, llm: BaseChatModel, **kwargs):
        super().__init__(llm)

    @staticmethod
    def get_client() -> MultiServerMCPClient:
        # Get Notion API credentials from environment variables
        notion_token = os.getenv("NOTION_TOKEN")
        notion_version = os.getenv("NOTION_VERSION", "2022-06-28")
        
        if not notion_token:
            raise ValueError("NOTION_TOKEN environment variable is required")
            
        # Construct the headers JSON string
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": notion_version
        }
        return MultiServerMCPClient(
            {
                "notion-mcp":{
                    "command": "npx",
                    "args": ["-y", "@notionhq/notion-mcp-server"],
                    "env": {"OPENAPI_MCP_HEADERS": json.dumps(headers)},
                    "transport": "stdio"
                }
            }
        )


    async def export(self, summary: Summary) -> None:
        try:
            # Initialize the state with the summary
            initial_state = State(
                messages=[],
                summary=summary,
                page_id="",
                block_ids=[],
                verification_results={},
                remaining_steps=40,
            )
            client = NotionMcpExporter.get_client()
            tools = await client.get_tools()

            agent = create_react_agent(
                model="openai:gpt-4.1-mini",
                state_schema=State,
                tools=tools,
            )
            parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
            initial_state["messages"] = add_messages(
                initial_state["messages"],
                SystemMessage(content=self._prompt_for_notion_mcp(summary, parent_page_id))
                )

            result = await agent.ainvoke(input=initial_state, config={"recursion_limit": 50})

            # Print the results
            for m in result["messages"]:
                print(m.pretty_print())

        except Exception as e:
            print(f"Error during export: {str(e)}")
            raise


    def _prompt_for_notion_mcp(self, summary: Summary, parent_page_id: str) -> str:
        prompt = f"""You are a Notion API expert. Follow these exact steps to create and format a Notion page:
                1. Create Page (First Step):
                - use the parent_page_id to create a new page
                - Create a clear title based on: {str(summary)}
                - No emojis or special characters
                - Store the returned page_id

                2. Add Blocks (Second Step):
                Use add_blocks tool with the page_id from step 1
                Important Guidelines:
                - Keep requests under 100 blocks
                - for latex equations, use the following format: $...$ for inline math
                - Never use null values
                - Always include all required fields for each block type
                - Ensure proper nesting of objects
                - Use appropriate block types for different content

                3. Verify (Final Step):
                - Check page title and parent_page_id
                - Verify all blocks are properly formatted
                - Ensure all content is properly structured
                - Report any issues found

                Here is the parent_page_id:
                {parent_page_id}

                Content to format:
                {str(summary)}"""
        return prompt


class ExporterType(Enum):
    MARKDOWN = "markdown"
    NOTION_MCP = "notion_mcp"

class ExporterFactory:
    _exporters: Dict[ExporterType, Type[Exporter]] = {
        ExporterType.MARKDOWN: MarkdownExporter,
        ExporterType.NOTION_MCP: NotionMcpExporter
    }

    @classmethod
    def get_exporter(cls, exporter_type: ExporterType, **kwargs) -> Exporter:
        if exporter_type not in cls._exporters:
            raise ValueError(f"Exporter type '{exporter_type}' not supported. Available exporters: {list(cls._exporters.keys())}")
        return cls._exporters[exporter_type](**kwargs)