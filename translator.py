import os

from unstructured.partition.pdf import partition_pdf
from typing import List, Dict, Any
import logging
import openai

from unstructured.partition.utils.constants import PartitionStrategy
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

from docx_writer import DocxWriter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def partition_pdf_file(
    pdf_path: str,
    include_page_breaks: bool = True,
    strategy: str = PartitionStrategy.HI_RES,
    output_path: str = "output.docx",
) -> List[Dict[str, Any]]:
    """
    Partition a PDF file into structured elements using the unstructured library.
    
    Args:
        pdf_path (str): Path to the PDF file to partition
        include_page_breaks (bool): Whether to include page breaks in the output
        include_metadata (bool): Whether to include metadata in the output
        strategy (str): Partitioning strategy ('fast', 'hi_res', or 'ocr_only')
        output_path (str): Partitioning strategy ('fast', 'hi_res', or 'ocr_only')

    Returns:
        List[Dict[str, Any]]: List of partitioned elements with their content and metadata
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: For other PDF processing errors
    """
    try:
        logger.info(f"Starting PDF partitioning for: {pdf_path}")
        
        # Partition the PDF
        elements = partition_pdf(
            filename=pdf_path,
            include_page_breaks=include_page_breaks,
            strategy=strategy,
            # Using pdf format to find embedded image blocks
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True,
            infer_table_structure=True,

        )
        cur_page = 0

        # Convert elements to a more structured format
        text = ""
        docx_writer = DocxWriter(output_path)
        
        for i, el in enumerate(elements):
            page_num = el.metadata.page_number
            if page_num is not None and page_num != cur_page:
                cur_page = page_num

            if cur_page % 2 == 0:
                if text == "":
                    continue

                docx_writer.write_chunk(
                    translated_text=translate_english_to_vietnamese(text),
                )
                # chunks = chunk_text_semantically(text)
                # last_chunk = chunks[-1]
                text = ""

                # if last_chunk.endswith("."):
                #     text = last_chunk
                #     chunks = chunks[:-1]
                #
                # for chunk in chunks:
                #     docx_writer.write_chunk(
                #         translated_text=translate_english_to_vietnamese(chunk),
                #     )

            category = el.category
            if category == "Image" and el.metadata.image_base64 is not None:
                # Write to DOCX immediately
                docx_writer.write_chunk(
                    translated_text=translate_english_to_vietnamese(text),
                )
                docx_writer.add_image_from_base64(
                    base64_string=el.metadata.image_base64,
                )
                text = ""
                continue
            elif category in ["Title", "ListItem", "Table"]:
                text += "\n" + el.text
            elif category in ["NarrativeText", "UncategorizedText"]:
                text += " " + el.text
            else:
                text += " " + el.text

    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(f"Error partitioning PDF {pdf_path}: {str(e)}")
        raise Exception(f"Failed to partition PDF: {str(e)}")


def chunk_text_semantically(
    text: str,
    model: str = "text-embedding-3-small",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Chunk text into semantically meaningful segments using LangChain's SemanticChunker.

    Args:
        text (str): Input text string to be chunked
        model (str): OpenAI embedding model to use for semantic chunking
        chunk_size (int): Target size for each chunk in characters
        chunk_overlap (int): Number of characters to overlap between chunks

    Returns:
        List[str]: List of semantically meaningful text chunks

    Raises:
        Exception: For chunking errors or API issues
    """
    try:
        logger.info(f"Starting semantic chunking of text (length: {len(text)} characters)")

        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings(model=model)

        # Create semantic chunker
        chunker = SemanticChunker(
            embeddings=embeddings,
            min_chunk_size=chunk_size,
        )

        # Split text into semantic chunks
        text_chunks = chunker.split_text(text)

        logger.info(f"Successfully created {len(text_chunks)} semantic chunks")
        return text_chunks

    except Exception as e:
        logger.error(f"Error during semantic chunking: {str(e)}")
        raise Exception(f"Failed to chunk text semantically: {str(e)}")


def _get_translation_prompt(source_lang: str, target_lang: str) -> str:
    """Generate the system prompt for translation."""
    return f"""You are a professional translator. Translate the following text from {source_lang} to {target_lang}.

CRITICAL RULES:
- TRANSLATE ONLY. Do not add explanations, summaries, or commentary
- Preserve exact formatting: line breaks, paragraphs, bullet points, lists
- Keep ALL text in parentheses ( ) unchanged - DO NOT translate
- Preserve numbers, dates, mathematical expressions exactly
- Maintain original structure and layout
- Use proper {target_lang} grammar and vocabulary
- Keep technical terms accurate and appropriate for {target_lang}

OUTPUT: Only return the translated text with identical formatting. Do not include any instructions, explanations, or extra text. Only return the result."""


def translate_english_to_vietnamese(text: str, model: str = "openai/gpt-oss-120b", api_key: str = None) -> str:
    """
    Translate English text to Vietnamese using OpenAI LLM.

    Args:
        text (str): The English text to translate.
        model (str): The OpenAI model to use for translation.
        api_key (str): OpenAI API key. If None, uses openai.api_key set elsewhere.

    Returns:
        str: The translated Vietnamese text.

    Raises:
        Exception: If translation fails.
    """
    if text == "":
        return None

    if api_key:
        openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        client = openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the text to Vietnamese with proper formatting suitable for document use. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Maintain proper paragraph breaks and sentence structure 3) Use appropriate punctuation and spacing 4) Format the output to be clean and professional for copying to document files 5) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 6) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more."
                },
                {
                    "role": "user",
                    "content": f"Translate this text to Vietnamese: {text}"
                }
            ],
            max_tokens=4000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI translation failed: {str(e)}")
        return None