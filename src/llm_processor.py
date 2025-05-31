from src.content_analyzer import AnalyzedContent
from typing import List, Dict, Any, Optional
from langchain_core.runnables import Runnable, RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel
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
    questions: List[str]

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
        system_message = """You are an expert educational content summarizer for university students.
            Your task is to analyze educational content and extract key concepts and ideas.

            Guidelines:
            1. For each concept, provide a detailed explanation of the concept, including examples and applications.
            2. For each concept, provide a summary of the concept.
            3. For each concept, if it uses mathematical expressions, provide a list of examples that illustrate the concept.
            4. For each concept, provide a list of key insights that are important to remember.
            5. For each concept, provide a list of questions that are important to ask yourself when learning the concept.
            6. For each concept, if it expose new terms, provide a list of key terms that are important to remember.
            7. Format all mathematical expressions using LaTeX notation:
               - Use $...$ for inline math
               - Use $$...$$ for display math
            
            Your output should be structured and well-organized, making it easy to understand the relationships between concepts.

            Here are the concepts to summarize:
            {concepts}
            """
        
        model = self.llm.with_structured_output(Summary)
        prompt = PromptTemplate.from_template(system_message)
        chain = prompt | model
        return chain

