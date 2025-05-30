import pytest
from src.content_analyzer import AnalyzedContent
import logging


logger = logging.getLogger(__name__)

    
def test_analyze_slide_title(content_analyzer, sample_slides):
    """Test analyzing a title slide."""
    analyzed = content_analyzer.analyze_slide(sample_slides[0])
    
    assert analyzed.slide_number == 1
    assert analyzed.main_text == "Title Slide\n• First point\n• Second point"
    assert analyzed.topic == "Title Slide"
    assert analyzed.metadata == {"type": "title"}

def test_analyze_slide_content(content_analyzer, sample_slides):
    """Test analyzing a content slide."""
    analyzed = content_analyzer.analyze_slide(sample_slides[1])
    
    assert analyzed.slide_number == 2
    assert analyzed.main_text == "Content Slide\n• Main point 1\n• Main point 2\n• Main point 3"
    assert analyzed.topic == "Content Slide"
    assert analyzed.metadata == {"type": "content"}

def test_analyze_slide_with_image(content_analyzer, sample_slides):
    """Test analyzing a slide with an image."""
    analyzed = content_analyzer.analyze_slide(sample_slides[2])
    
    assert analyzed.slide_number == 3
    assert analyzed.main_text == "Image Slide with some text"
    assert analyzed.topic == "Image Slide with some text"
    assert analyzed.metadata == {"type": "image"}

def test_analyze_presentation(content_analyzer, sample_slides):
    """Test analyzing a complete presentation."""
    analyzed_slides = content_analyzer.analyze_presentation(sample_slides)
    
    assert len(analyzed_slides) == 3
    assert all(isinstance(slide, AnalyzedContent) for slide in analyzed_slides)
    assert [slide.slide_number for slide in analyzed_slides] == [1, 2, 3]

def test_identify_topic(content_analyzer):
    """Test topic identification."""
    text = "Main topic. Supporting point. Another point."
    topic = content_analyzer._identify_topic(text)
    
    assert topic == "Main topic"

def test_identify_topic_empty_text(content_analyzer):
    """Test topic identification with empty text."""
    topic = content_analyzer._identify_topic("")
    assert topic is None

def test_identify_topic_with_multiple_delimiters(content_analyzer):
    """Test topic identification with various delimiters."""
    text = """Main Topic!
    Supporting point.
    Another point;
    Final point:"""
    
    topic = content_analyzer._identify_topic(text)
    assert topic == "Main Topic"

def test_identify_topic_with_newlines(content_analyzer):
    """Test topic identification with newline delimiters."""
    text = """First line
    Second line
    Third line"""
    
    topic = content_analyzer._identify_topic(text)
    assert topic == "First line"
