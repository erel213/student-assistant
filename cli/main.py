import argparse
import asyncio
import os
from typing import Dict, Type
from src.presentation_processor import PresentationProcessor
from src.llm_processor import LLMProcessor, Summary
from langchain.chat_models import init_chat_model
from src.exporter import ExporterFactory, ExporterType
from src.content_analyzer import ContentAnalyzer



def load_api_key() -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please set it using 'export OPENAI_API_KEY=your-key'")
    return api_key

def main():
    parser = argparse.ArgumentParser(description='Notion Summary Automation CLI')
    parser.add_argument('--export_path', type=str, required=False,
                      help='Output file path')
    parser.add_argument('--source_path', type=str, required=True,
                      help='Source file path')
    parser.add_argument('--exporter', type=ExporterType, default=ExporterType.MARKDOWN,
                      help='Exporter type')

    args = parser.parse_args()

    # Initialize LLM
    llm = init_chat_model("gpt-4.1-mini", model_provider="openai", temperature=0.5)
    content_analyzer = ContentAnalyzer()
    presentation_processor = PresentationProcessor()

    slides = presentation_processor.process_file(args.source_path)
    analyzed_slides = content_analyzer.analyze_presentation(slides)

    llm_processor = LLMProcessor(llm)
    process_chain = llm_processor.process_presentation()
    summary: Summary = process_chain.invoke(analyzed_slides)

    
    # Create exporter
    exporter = ExporterFactory.get_exporter(
        args.exporter,
        llm=llm,
        export_path=args.export_path
    )
    
    # Export the summary
    asyncio.run(exporter.export(summary))
    print(f"Summary successfully exported to {args.export_path}")


if __name__ == '__main__':
    main() 
