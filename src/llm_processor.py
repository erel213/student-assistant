from src.content_analyzer import AnalyzedContent
from typing import List, Dict, Any, Optional
from langchain_core.runnables import Runnable, RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
import getpass
import os

class Concept(BaseModel):
    topic: str
    key_ideas: List[str]

class Concepts(BaseModel):
    concepts: List[Concept]

class TopicSummary(BaseModel):
    topic: str
    examples: Optional[List[str]]
    key_terms: Optional[List[str]]
    detailed_explanation: Optional[str]
    summary: str
    key_insights: List[str]

class Summary(BaseModel):
    topics: List[TopicSummary]

class LLMProcessor:
    def __init__(self, base_model: BaseChatModel):
        self.llm = base_model

    def process_presentation(self) -> RunnableSequence:
        """
        Process a presentation and return a chain that can be invoked.
        """
        # Create a chain that takes analyzed_slides and returns concepts
        concepts_chain = self.concepts_chain
        # Create a chain that takes concepts and returns summary
        summary_chain = self.summary_chain
        # Compose the chains together
        return RunnableSequence(concepts_chain, summary_chain)

    def concepts_chain(self, analyzed_slides: List[AnalyzedContent]) -> Runnable:
        """
        Extract the concepts from the analyzed slides using the LLM, grouped by topic.
        """
        system_message = """You are an expert educational content analyzer and concept extractor.
            Your primary task is to analyze educational slides and extract their core concepts and supporting ideas.            

            For each slide:
            1. Identify the main concept 
            2. Extract key supporting ideas that elaborate on the main concept
            3. Ensure the concept accurately represents the slide's primary message
            4. Maintain clarity and precision in your extraction
            5. Use appropriate domain-specific terminology
            6. Format all mathematical expressions using LaTeX notation:
               - Use $...$ for inline math
               - Use $$...$$ for display math
            
            Your output should be structured to clearly show the relationship between the main concept and its supporting ideas.

            Here are the slides to analyze:
            {analyzed_slides}
            """

        model = self.llm.with_structured_output(Concepts)
        prompt = PromptTemplate.from_template(system_message)
        chain = prompt | model
        return chain

    def summary_chain(self, concepts: Concepts) -> Runnable:
        """
        Extract the summary from the concepts using the LLM.
        """
        system_message = """You are an expert university lecturer writing comprehensive study notes for students.
            Your goal is to deeply teach each concept — not just summarize it. Write as if you are explaining the material
            to a student who is encountering it for the first time and needs to truly understand it, not just memorize it.

            For each concept, use whatever teaching approach best serves understanding: build intuition before formalism,
            show worked examples, highlight common misconceptions, connect to related ideas, or explain the "why" behind
            the concept. Be thorough — a student should be able to learn the concept solely from your output.

            Guidelines:
            1. detailed_explanation: Provide a thorough, in-depth explanation. Use the teaching style and structure
               that best conveys the concept — there is no prescribed format. Depth and clarity are the priority.
            2. summary: A concise recap of the essential idea a student must take away.
            3. examples: Worked examples where relevant (especially for math, algorithms, or processes).
            4. key_terms: Any new vocabulary or notation introduced, with brief definitions.
            5. key_insights: The most important non-obvious takeaways a student might miss.
            6. Format all mathematical expressions using LaTeX notation:
               - Use $...$ for inline math
               - Use $$...$$ for display math

            Here are the concepts to summarize:
            {concepts}
            """
        
        model = self.llm.with_structured_output(Summary)
        prompt = PromptTemplate.from_template(system_message)
        chain = prompt | model
        return chain

