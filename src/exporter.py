from abc import ABC, abstractmethod
from src.llm_processor import Summary
from langchain.prompts import PromptTemplate
from langchain.chat_models.base import BaseChatModel
from enum import Enum
from typing import Dict, Type
from langchain_core.output_parsers import StrOutputParser

class Exporter(ABC):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    @abstractmethod
    def export(self, summary: Summary) -> None:
        pass

class MarkdownExporter(Exporter):
    def __init__(self, llm: BaseChatModel, export_path: str):
        super().__init__(llm)
        self.export_path = export_path

    def export(self, summary: Summary) -> None:
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


class ExporterType(Enum):
    MARKDOWN = "markdown"

class ExporterFactory:
    _exporters: Dict[ExporterType, Type[Exporter]] = {
        ExporterType.MARKDOWN: MarkdownExporter
    }

    @classmethod
    def get_exporter(cls, exporter_type: ExporterType, **kwargs) -> Exporter:
        if exporter_type not in cls._exporters:
            raise ValueError(f"Exporter type '{exporter_type}' not supported. Available exporters: {list(cls._exporters.keys())}")
        return cls._exporters[exporter_type](**kwargs)