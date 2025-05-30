from typing import List, Dict, Optional
from dataclasses import dataclass
from src.presentation_processor import SlideContent
import re

@dataclass
class AnalyzedContent:
    """Represents the analyzed content from a slide with enhanced structure and metadata."""
    slide_number: int
    main_text: str
    topic: Optional[str]
    metadata: Dict[str, str]

class ContentAnalyzer:
    """Analyzes and structures presentation content for LLM processing."""

    def __init__(self):
        # Common delimiters for splitting text into sentences
        self.sentence_delimiters = ['.', '!', '?', '\n', ';', ':', '•', '-', '*']
        # Escape special characters and create pattern
        escaped_delimiters = [re.escape(d) for d in self.sentence_delimiters]
        self.sentence_pattern = re.compile(f'[{"".join(escaped_delimiters)}]')

    def analyze_slide(self, slide: SlideContent) -> AnalyzedContent:
        """
        Analyzes a single slide and returns structured content.
        
        Args:
            slide: SlideContent object containing raw slide data
            
        Returns:
            AnalyzedContent object with enhanced structure and metadata
        """
        # Extract key points from the text
        
        # Identify topic if possible
        topic = self._identify_topic(slide.text)
        
        return AnalyzedContent(
            slide_number=slide.slide_number,
            main_text=slide.text,
            topic=topic,
            metadata=slide.metadata
        )
    
    def analyze_presentation(self, slides: List[SlideContent]) -> List[AnalyzedContent]:
        """
        Analyzes a complete presentation and returns structured content for all slides.
        
        Args:
            slides: List of SlideContent objects
            
        Returns:
            List of AnalyzedContent objects
        """
        analyzed_slides = []
        
        for slide in slides:
            analyzed_slide = self.analyze_slide(slide)
            analyzed_slides.append(analyzed_slide)

        return analyzed_slides

    
    def _extract_key_points(self, text: str) -> List[str]:
        """
        Extracts key points from the slide text.
        
        Args:
            text: Slide text content
            
        Returns:
            List of key points
        """
        # Split text into sentences using multiple delimiters
        sentences = []
        for part in self.sentence_pattern.split(text):
            part = part.strip()
            if part:
                sentences.append(part)
        
        # Simple heuristic: consider sentences with bullet points or numbers as key points
        key_points = []
        for sentence in sentences:
            if sentence.startswith(('•', '-', '*', '1.', '2.', '3.')):
                key_points.append(sentence)
        
        # If no bullet points found, take first 3 sentences as key points
        if not key_points and sentences:
            key_points = sentences[:3]
        
        return key_points
    
    def _identify_topic(self, text: str) -> Optional[str]:
        """
        Attempts to identify the main topic of the slide.
        
        Args:
            text: Slide text content
            
        Returns:
            Topic string or None if not identifiable
        """
        # Split text using the same delimiters as key points
        sentences = []
        for part in self.sentence_pattern.split(text):
            part = part.strip()
            if part:
                sentences.append(part)
        
        if sentences:
            return sentences[0]
        return None
    
