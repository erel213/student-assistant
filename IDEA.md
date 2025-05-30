# Presentation to Notion Summary Automation

## Overview
This project aims to create a CLI tool that automates the process of extracting information from school presentations, analyzing them using LLMs, and creating structured summaries in Notion.

## Core Components

### 1. CLI Interface
- Command-line interface for easy interaction
- Support for various input formats (PDF, PPTX, etc.)
- Configuration options for Notion integration

### 2. Presentation Processing
- Extract text and content from presentation files
- Handle different presentation formats
- Maintain slide structure and hierarchy

### 3. LLM Analysis (Using LangChain)
- Process presentation content through LLM
- Identify key subjects and topics
- Generate structured summaries
- Extract important points and relationships

### 4. Notion Integration
- Create new pages in Notion
- Structure content hierarchically
- Include metadata and tags
- Link related content

## Technical Stack
- Python as the primary language
- LangChain for LLM orchestration
- Notion API for content management
- PDF/PPTX processing libraries
- CLI framework (e.g., Click or Typer)

## Workflow
1. User inputs presentation file through CLI
2. System extracts content from presentation
3. LangChain processes content to identify subjects
4. LLM generates structured summary
5. System creates Notion page with summary
6. Returns success/failure status

## Features
- Support for multiple presentation formats
- Configurable LLM models
- Customizable Notion page templates
- Error handling and logging
- Progress tracking
- Batch processing capability

## Future Enhancements
- Support for additional file formats
- Custom summary templates
- Integration with other note-taking platforms
- Collaborative features
- Automated tagging system
- Version control for summaries

## Requirements
- Python 3.8+
- Notion API key
- LLM API access
- Required Python packages:
  - langchain
  - notion-client
  - python-pptx
  - PyPDF2
  - click/typer
