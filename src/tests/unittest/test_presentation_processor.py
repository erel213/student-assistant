import pytest
from pathlib import Path
from src.presentation_processor import PresentationProcessor, SlideContent
import os

def test_process_file_nonexistent(processor):
    """Test processing a non-existent file."""
    with pytest.raises(FileNotFoundError):
        processor.process_file("nonexistent.pdf")

def test_process_file_unsupported_format(processor, temp_dir):
    """Test processing a file with unsupported format."""
    unsupported_file = temp_dir / "test.txt"
    unsupported_file.write_text("test content")
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        processor.process_file(unsupported_file)

def test_process_pdf(processor, sample_pdf):
    """Test processing a PDF file."""
    slides = processor.process_file(sample_pdf)
    
    assert len(slides) == 2  # We created 2 pages
    assert all(isinstance(slide, SlideContent) for slide in slides)
    assert slides[0].slide_number == 1
    assert slides[1].slide_number == 2
    assert slides[0].metadata['file_type'] == 'pdf'
    assert slides[0].metadata['page_count'] == 2

def test_process_pptx(processor, sample_pptx):
    """Test processing a PPTX file."""
    slides = processor.process_file(sample_pptx)
    
    assert len(slides) == 2  # We created 2 slides
    assert all(isinstance(slide, SlideContent) for slide in slides)
    assert slides[0].slide_number == 1
    assert slides[1].slide_number == 2
    assert "First Slide" in slides[0].text
    assert "Second Slide" in slides[1].text
    assert slides[0].metadata['file_type'] == 'pptx'
    assert slides[0].metadata['slide_count'] == 2

def test_slide_content_structure(processor, sample_pptx):
    """Test the structure of SlideContent objects."""
    slides = processor.process_file(sample_pptx)
    slide = slides[0]
    
    assert hasattr(slide, 'slide_number')
    assert hasattr(slide, 'text')
    assert hasattr(slide, 'images')
    assert hasattr(slide, 'metadata')
    assert isinstance(slide.images, list)
    assert isinstance(slide.metadata, dict)

def test_pdf_content_extraction(processor, sample_pdf):
    """Test content extraction from PDF."""
    slides = processor.process_file(sample_pdf)
    
    # PDF pages are blank in our test, but we can verify structure
    assert len(slides) > 0
    assert all(isinstance(slide.text, str) for slide in slides)
    assert all(len(slide.images) == 0 for slide in slides)  # No images in our test PDF

def test_pptx_content_extraction(processor, sample_pptx):
    """Test content extraction from PPTX."""
    slides = processor.process_file(sample_pptx)
    
    # Verify text content
    assert "First Slide" in slides[0].text
    assert "This is the first slide content" in slides[0].text
    assert "Second Slide" in slides[1].text
    assert "This is the second slide content" in slides[1].text
