import os
import logging
from typing import List, Dict, Any, Optional
import re

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.utils.constants import PartitionStrategy
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import openai

from docx_writer import DocxWriter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _process_text_buffer(text_buffer: str) -> tuple[str, str]:
    """
    Process text buffer to handle sentence boundaries intelligently.

    Args:
        text_buffer (str): Text to process

    Returns:
        tuple[str, str]: (complete_text, remaining_incomplete_text)
    """
    if not text_buffer or text_buffer.rstrip().endswith(('.', '!', '?')):
        # Text is complete or already ends with sentence ending
        return text_buffer, ""

    # Find the last complete sentence
    # Use a more robust regex to find sentence endings
    sentence_pattern = r'([.!?])\s+'
    matches = list(re.finditer(sentence_pattern, text_buffer))

    if not matches:
        # No sentence endings found, return entire text as incomplete
        return "", text_buffer

    # Get the position of the last sentence ending
    last_match = matches[-1]
    complete_end = last_match.end()

    # Split into complete and incomplete parts
    complete_text = text_buffer[:complete_end].rstrip()
    remaining_text = text_buffer[complete_end:].strip()

    return complete_text, remaining_text

class Translator:
    """A class for translating PDF documents from English to Vietnamese."""

    def __init__(self,
                 openai_api_key: str = None,
                 model: str = "openai/gpt-oss-120b",
                 base_url: str = "https://api.groq.com/openai/v1",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the Translator.
        
        Args:
            openai_api_key (str): OpenAI API key. If None, uses environment variable.
            model (str): The OpenAI model to use for translation.
            base_url (str): Base URL for the OpenAI API.
            chunk_size (int): Target size for each chunk in characters.
            chunk_overlap (int): Number of characters to overlap between chunks.
            embedding_model (str): OpenAI embedding model for semantic chunking.
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model

        # Initialize OpenAI client
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            logger.warning("No OpenAI API key provided. Translation will fail.")
            self.client = None

    def partition_pdf_file(self,
                           pdf_path: str,
                           include_page_breaks: bool = True,
                           strategy: str = PartitionStrategy.HI_RES,
                           output_path: str = "output.docx") -> List[Dict[str, Any]]:
        """
        Partition a PDF file into structured elements and translate to Vietnamese.
        
        Args:
            pdf_path (str): Path to the PDF file to partition
            include_page_breaks (bool): Whether to include page breaks in the output
            strategy (str): Partitioning strategy ('fast', 'hi_res', or 'ocr_only')
            output_path (str): Path for the output DOCX file

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

            # Process and translate the elements
            self._process_elements(elements, output_path)

            logger.info(f"PDF processing and translation completed. Output saved to: {output_path}")

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            logger.error(f"Error partitioning PDF {pdf_path}: {str(e)}")
            raise Exception(f"Failed to partition PDF: {str(e)}")

    def _process_elements(self, elements: List[Any], output_path: str):
        """
        Process partitioned elements and translate them to Vietnamese.
        
        Args:
            elements (List[Any]): List of partitioned PDF elements
            output_path (str): Path for the output DOCX file
        """
        current_page = 0
        text_buffer = ""
        docx_writer = DocxWriter(output_path)
        
        for element in elements:
            page_num = element.metadata.page_number
            if page_num is not None and page_num != current_page:
                current_page = page_num
            
            # Process text on even pages
            if current_page % 2 == 0:
                if text_buffer:
                    # Process text buffer and handle sentence boundaries
                    text_buffer, remaining_text = _process_text_buffer(text_buffer)
                    
                    # Translate and write complete text
                    if text_buffer:
                        translated_text = self.translate_english_to_vietnamese(text_buffer)
                        if translated_text:
                            docx_writer.write_chunk(translated_text=translated_text)
                    
                    # Keep remaining incomplete sentence for next iteration
                    text_buffer = remaining_text
            
            # Handle different element categories
            category = element.category
            if category == "Image" and element.metadata.image_base64 is not None:
                # Write any pending text first
                if text_buffer.strip():
                    translated_text = self.translate_english_to_vietnamese(text_buffer)
                    if translated_text:
                        docx_writer.write_chunk(translated_text=translated_text)
                
                # Add image to document
                docx_writer.add_image_from_base64(
                    base64_string=element.metadata.image_base64,
                )
                text_buffer = ""
                
            elif category in ["Title", "ListItem", "Table"]:
                text_buffer += "\n" + element.text
            elif category in ["NarrativeText", "UncategorizedText"]:
                text_buffer = f"{text_buffer} {element.text}"
            elif category in [ 'PageBreak']:
                pass
        
        # Process any remaining text
        if text_buffer.strip():
            translated_text = self.translate_english_to_vietnamese(text_buffer)
            if translated_text:
                docx_writer.write_chunk(translated_text=translated_text)

    def chunk_text_semantically(self, text: str) -> List[str]:
        """
        Chunk text into semantically meaningful segments using LangChain's SemanticChunker.

        Args:
            text (str): Input text string to be chunked

        Returns:
            List[str]: List of semantically meaningful text chunks

        Raises:
            Exception: For chunking errors or API issues
        """
        try:
            logger.info(f"Starting semantic chunking of text (length: {len(text)} characters)")

            # Initialize OpenAI embeddings
            embeddings = OpenAIEmbeddings(model=self.embedding_model)

            # Create semantic chunker
            chunker = SemanticChunker(
                embeddings=embeddings,
                min_chunk_size=self.chunk_size,
            )

            # Split text into semantic chunks
            text_chunks = chunker.split_text(text)

            logger.info(f"Successfully created {len(text_chunks)} semantic chunks")
            return text_chunks

        except Exception as e:
            logger.error(f"Error during semantic chunking: {str(e)}")
            raise Exception(f"Failed to chunk text semantically: {str(e)}")

    def translate_english_to_vietnamese(self, text: str) -> Optional[str]:
        """
        Translate English text to Vietnamese using OpenAI LLM.

        Args:
            text (str): The English text to translate.

        Returns:
            Optional[str]: The translated Vietnamese text, or None if translation fails.

        Raises:
            Exception: If translation fails.
        """
        if not text or text.strip() == "":
            return None

        if not self.client:
            logger.error("No OpenAI client available. Check API key.")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional translator. Translate the following text to Vietnamese and format the output for direct use in a Microsoft Word (.docx) document.\n\n"
                            "CRITICAL RULES:\n"
                            "- ONLY return the translated text. Do not add explanations, summaries, or any extra content.\n"
                            "- Preserve all original formatting: line breaks, paragraphs, bullet points, numbered lists, tables, and headings.\n"
                            "- Use proper Vietnamese grammar, vocabulary, and punctuation suitable for formal documents.\n"
                            "- Maintain the structure and layout so the translation can be copied directly into a .docx file without further editing.\n"
                            "- Keep all keywords in parentheses ( )\n"
                            "- Preserve numbers, dates, and mathematical expressions exactly as in the original.\n"
                            "- Ensure the output is clean, professional, and ready for use in a Word document."
                        )
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

# Convenience functions for backward compatibility
def partition_pdf_file(pdf_path: str, **kwargs) -> List[Dict[str, Any]]:
    """Backward compatibility function."""
    translator = Translator()
    return translator.partition_pdf_file(pdf_path, **kwargs)


def chunk_text_semantically(text: str, **kwargs) -> List[str]:
    """Backward compatibility function."""
    translator = Translator(**kwargs)
    return translator.chunk_text_semantically(text)


def translate_english_to_vietnamese(text: str, **kwargs) -> Optional[str]:
    """Backward compatibility function."""
    translator = Translator(**kwargs)
    return translator.translate_english_to_vietnamese(text)
