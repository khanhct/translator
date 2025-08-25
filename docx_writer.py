from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn
from typing import List, Dict, Optional
import logging
import os
import base64
import io
from PIL import Image

logger = logging.getLogger(__name__)


class DocxWriter:
    """Handles writing translated content to DOCX format while preserving layout."""
    
    def __init__(self, output_path: str = None):
        # Check python-docx version and capabilities
        self._check_docx_compatibility()
        
        self.document = Document()
        self._setup_document_styles()
        self.output_path = output_path
        self.chunk_count = 0
        self.is_incremental_mode = output_path is not None
        
        # Track progress for incremental writing
        self.total_chunks = 0
        self.completed_chunks = 0
        
        if self.is_incremental_mode:
            logger.info(f"DocxWriter initialized in incremental mode for: {output_path}")
    
    def _check_docx_compatibility(self):
        """Check python-docx version and log compatibility information."""
        try:
            import docx
            version = getattr(docx, '__version__', 'unknown')
            logger.info(f"python-docx version: {version}")
            
            # Check for key features - use a safer approach
            try:
                from docx.styles.styles import ParagraphStyle
                has_space_after = hasattr(ParagraphStyle, 'space_after')
            except (ImportError, AttributeError):
                # Fallback: check if we can create a style and test space_after
                try:
                    test_doc = docx.Document()
                    test_style = test_doc.styles.add_style('TestStyle', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
                    has_space_after = hasattr(test_style, 'space_after')
                except:
                    has_space_after = False
            
            logger.info(f"space_after support: {has_space_after}")
            
            if not has_space_after:
                logger.warning("python-docx version may not support space_after attribute")
                logger.info("Consider upgrading to python-docx >= 0.8.11 for full feature support")
                
        except ImportError as e:
            logger.error(f"Could not import python-docx: {e}")
        except Exception as e:
            logger.warning(f"Could not check python-docx compatibility: {e}")
        
    def _setup_document_styles(self):
        """Setup document styles for different content types."""
        # Check python-docx version for compatibility
        try:
            import docx
            docx_version = getattr(docx, '__version__', '0.0.0')
            has_space_after = True
            logger.info(f"python-docx version: {docx_version}")
        except ImportError:
            docx_version = '0.0.0'
            has_space_after = False
            logger.warning("Could not determine python-docx version")
        
        # Header style
        header_style = self.document.styles.add_style('CustomHeader', WD_STYLE_TYPE.PARAGRAPH)
        header_style.font.size = Pt(16)
        header_style.font.bold = True
        if has_space_after and hasattr(header_style, 'space_after'):
            header_style.space_after = Pt(12)
        
        # Title style
        title_style = self.document.styles.add_style('CustomTitle', WD_STYLE_TYPE.PARAGRAPH)
        title_style.font.size = Pt(14)
        title_style.font.bold = True
        if has_space_after and hasattr(title_style, 'space_after'):
            title_style.space_after = Pt(10)
        
        # Normal text style
        normal_style = self.document.styles.add_style('CustomNormal', WD_STYLE_TYPE.PARAGRAPH)
        normal_style.font.size = Pt(12)
        if has_space_after and hasattr(normal_style, 'space_after'):
            normal_style.space_after = Pt(6)
        
        # Footer style
        footer_style = self.document.styles.add_style('CustomFooter', WD_STYLE_TYPE.PARAGRAPH)
        footer_style.font.size = Pt(9)
        footer_style.font.italic = True
        if has_space_after and hasattr(footer_style, 'space_after'):
            footer_style.space_after = Pt(6)
        
        # Table header style
        table_header_style = self.document.styles.add_style('CustomTableHeader', WD_STYLE_TYPE.PARAGRAPH)
        table_header_style.font.size = Pt(10)
        table_header_style.font.bold = True
        if has_space_after and hasattr(table_header_style, 'space_after'):
            table_header_style.space_after = Pt(3)
    
    def initialize_document_for_incremental_writing(self, total_chunks: int, title: str = "", 
                                                   source_lang: str = "English", target_lang: str = "Vietnamese"):
        """Initialize the document for incremental chunk writing."""
        self.total_chunks = total_chunks
        self.completed_chunks = 0
        
        # Add metadata
        self.add_metadata(
            title=title or f"Translated Document ({source_lang} -> {target_lang})",
            author="PDF Translator App",
            subject=f"Translation from {source_lang} to {target_lang}"
        )
        
        # Add document header
        header = self.document.add_heading(f"Translated Document", level=1)
        header.style = self.document.styles['CustomTitle']
        
        # Add translation info
        info_para = self.document.add_paragraph(f"Translation: {source_lang} → {target_lang}")
        info_para.style = self.document.styles['CustomNormal']
        
        # Add progress placeholder that we'll update
        self.progress_paragraph = self.document.add_paragraph(f"Translation Progress: 0/{total_chunks} chunks completed")
        self.progress_paragraph.style = self.document.styles['CustomNormal']
        
        # Add separator
        self.document.add_paragraph("─" * 50).style = self.document.styles['CustomNormal']
        
        logger.info(f"Document initialized for incremental writing: {total_chunks} chunks expected")
    
    def write_chunk(self, translated_text: str = None, chunk_type: str = "text"):
        """Write a single translated chunk to the document and save immediately."""

        if translated_text is None:
            return

        try:
            # Add the translated content
            self._add_translated_chunk(translated_text, chunk_type)
            
            # Update progress
            self.completed_chunks += 1
            self._update_progress()
            
            # ✅ FIXED: Save after EVERY chunk to ensure immediate persistence
            if self.output_path:
                self._save_incremental_progress()
        except Exception as e:
            raise
    
    def _update_progress(self):
        """Update the progress paragraph in the document."""
        try:
            # Update the progress paragraph text
            progress_text = f"Translation Progress: {self.completed_chunks}/{self.total_chunks} chunks completed"
            if self.progress_paragraph and self.progress_paragraph.runs:
                # Clear existing text and add new text
                for run in self.progress_paragraph.runs:
                    run.text = ""
                self.progress_paragraph.runs[0].text = progress_text
            else:
                # Fallback: add a new progress paragraph
                self.progress_paragraph = self.document.add_paragraph(progress_text)
                self.progress_paragraph.style = self.document.styles['CustomNormal']
                
        except Exception as e:
            logger.warning(f"Could not update progress display: {e}")
    
    def _save_incremental_progress(self):
        """Save the document with current progress."""
        if not self.output_path:
            return
            
        try:
            self.document.save(self.output_path)
            completion_percent = (self.completed_chunks / self.total_chunks) * 100 if self.total_chunks > 0 else 0
            logger.info(f"✅ Chunk {self.completed_chunks} saved to file: {completion_percent:.1f}% complete ({self.completed_chunks}/{self.total_chunks} chunks)")
            
            # Verify file was actually written
            if os.path.exists(self.output_path):
                file_size = os.path.getsize(self.output_path)
                logger.info(f"📁 File verified: {self.output_path} ({file_size:,} bytes)")
            else:
                logger.warning(f"⚠️ File not found after save: {self.output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save incremental progress: {e}")
            # Don't raise exception here - we want translation to continue
    
    def finalize_incremental_document(self, translation_stats: Dict = None):
        """Finalize the document after all chunks are written."""
        try:
            # Update final progress
            self._update_progress()
            
            # Add completion timestamp
            import datetime
            completion_para = self.document.add_paragraph(
                f"\nTranslation completed on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            completion_para.style = self.document.styles['CustomNormal']
            
            # Add summary if stats provided
            if translation_stats:
                self.document.add_page_break()
                self.create_summary_page(translation_stats)
            
            # Final save
            if self.output_path:
                self.document.save(self.output_path)
                logger.info(f"Document finalized and saved: {self.output_path}")
                
        except Exception as e:
            logger.error(f"Failed to finalize document: {e}")
            raise
    
    def _apply_style_spacing(self, style, spacing_pt):
        """Apply spacing to a style in a version-compatible way."""
        try:
            if hasattr(style, 'space_after'):
                style.space_after = Pt(spacing_pt)
                return True
            else:
                # Fallback: try to set paragraph spacing through paragraph format
                logger.debug(f"space_after not available for style, using fallback method")
                return False
        except Exception as e:
            logger.warning(f"Could not apply spacing to style: {e}")
            return False
    
    def _add_paragraph_spacing(self, paragraph, spacing_pt):
        """Add spacing after a paragraph in a version-compatible way."""
        try:
            # Try to set spacing directly on the paragraph
            if hasattr(paragraph, 'space_after'):
                paragraph.space_after = Pt(spacing_pt)
                return True
            else:
                # Alternative: add empty paragraph with spacing
                empty_para = self.document.add_paragraph()
                if hasattr(empty_para, 'space_after'):
                    empty_para.space_after = Pt(spacing_pt)
                return True
        except Exception as e:
            logger.warning(f"Could not apply paragraph spacing: {e}")
            return False
        
    def write_translated_content(self, translated_chunks: List[Dict], original_layout: List[Dict]) -> Document:
        """Write translated content to DOCX while preserving original layout."""
        logger.info("Starting to write translated content to DOCX...")
        
        # Group chunks by page
        pages = self._group_chunks_by_page(translated_chunks, original_layout)
        
        for page_num, page_data in pages.items():
            logger.info(f"Processing page {page_num}")
            
            # Add page break if not first page
            if page_num > 1:
                self.document.add_page_break()
            
            # Write page content
            self._write_page_content(page_data)
        
        logger.info("DOCX document creation completed")
        return self.document
    
    def _group_chunks_by_page(self, translated_chunks: List[Dict], original_layout: List[Dict]) -> Dict[int, Dict]:
        """Group translated chunks by page number."""
        pages = {}
        
        for chunk in translated_chunks:
            page_num = chunk.get("page_number", 1)
            if page_num not in pages:
                pages[page_num] = {
                    "chunks": [],
                    "layout": self._find_page_layout(original_layout, page_num)
                }
            pages[page_num]["chunks"].append(chunk)
        
        # Sort chunks within each page
        for page_data in pages.values():
            page_data["chunks"].sort(key=lambda x: x.get("chunk_index", 0))
        
        return pages
    
    def _find_page_layout(self, original_layout: List[Dict], page_num: int) -> Optional[Dict]:
        """Find the original layout for a specific page."""
        for page in original_layout:
            if page.get("page_number") == page_num:
                return page
        return None
    
    def _write_page_content(self, page_data: Dict):
        """Write content for a single page."""
        chunks = page_data["chunks"]
        layout = page_data.get("layout", {})
        
        # Write page header if available
        if layout and "sections" in layout:
            self._write_page_sections(layout["sections"], chunks)
        else:
            # Fallback: write chunks sequentially
            for chunk in chunks:
                self._write_chunk(chunk)
    
    def _write_page_sections(self, sections: List[Dict], chunks: List[Dict]):
        """Write content organized by sections."""
        chunk_index = 0
        
        for section in sections:
            section_type = section.get("type", "text")
            
            # Find corresponding translated chunks
            section_chunks = []
            while chunk_index < len(chunks):
                chunk = chunks[chunk_index]
                if chunk.get("section_type") == section_type:
                    section_chunks.append(chunk)
                    chunk_index += 1
                else:
                    break
            
            # Write section content
            if section_chunks:
                self._write_section(section, section_chunks)
            else:
                # Write original section content if no translation available
                self._write_original_section(section)
    
    def _write_section(self, section: Dict, chunks: List[Dict]):
        """Write a section with its translated chunks."""
        section_type = section.get("type", "text")
        
        # Write section header/title
        if section_type in ["header", "title"]:
            header_text = " ".join(section.get("content", []))
            if header_text:
                paragraph = self.document.add_paragraph(header_text)
                paragraph.style = self.document.styles['CustomHeader']
        
        # Write section content
        for chunk in chunks:
            self._write_chunk(chunk)
    
    def _write_original_section(self, section: Dict):
        """Write original section content when translation is not available."""
        section_type = section.get("type", "text")
        content = " ".join(section.get("content", []))
        
        if not content:
            return
        
        if section_type in ["header", "title"]:
            paragraph = self.document.add_paragraph(content)
            paragraph.style = self.document.styles['CustomHeader']
        else:
            paragraph = self.document.add_paragraph(content)
            paragraph.style = self.document.styles['CustomNormal']
    
    def _write_chunk(self, chunk: Dict):
        """Write a single translated chunk (legacy method)."""
        translated_text = chunk.get("translated_text", "")
        chunk_type = chunk.get("section_type", "text")
        self._add_translated_chunk(translated_text, chunk_type)
    
    def _add_translated_chunk(self, translated_text: str, chunk_type: str = "text"):
        """Add a translated chunk to the document with appropriate styling."""
        if not translated_text.strip():
            return
        
        # Determine paragraph style based on chunk type
        if chunk_type == "header":
            style = 'CustomHeader'
        elif chunk_type == "title":
            style = 'CustomTitle'
        elif chunk_type == "footer":
            style = 'CustomFooter'
        elif chunk_type == "table_header":
            style = 'CustomTableHeader'
        else:
            style = 'CustomNormal'
        
        # Split text into paragraphs and write
        paragraphs = translated_text.split('\n\n')
        
        for para_text in paragraphs:
            para_text = para_text.strip()
            if para_text:
                paragraph = self.document.add_paragraph(para_text)
                paragraph.style = self.document.styles[style]
                
                # Preserve bullet points and lists
                if para_text.startswith('•') or para_text.startswith('-'):
                    try:
                        paragraph.style = self.document.styles['List Bullet']
                    except KeyError:
                        # Fallback if List Bullet style doesn't exist
                        paragraph.style = self.document.styles['CustomNormal']
        
        # Add some spacing after the chunk
        self.document.add_paragraph("")  # Empty paragraph for spacing
    
    def add_table_of_contents(self):
        """Add a table of contents to the document."""
        # Add TOC heading
        toc_heading = self.document.add_heading('Table of Contents', level=1)
        toc_heading.style = self.document.styles['CustomTitle']
        
        # Add TOC field (will be updated when document is opened in Word)
        paragraph = self.document.add_paragraph()
        run = paragraph.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar)
        
        instrText = OxmlElement('w:instrText')
        instrText.text = "TOC \\o \"1-3\" \\h \\z \\u"
        run._r.append(instrText)
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'separate')
        run._r.append(fldChar)
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar)
        
        # Add page break after TOC
        self.document.add_page_break()
    
    def add_metadata(self, title: str = "", author: str = "", subject: str = ""):
        """Add metadata to the document."""
        core_props = self.document.core_properties
        if title:
            core_props.title = title
        if author:
            core_props.author = author
        if subject:
            core_props.subject = subject
    
    def save_document(self, output_path: str):
        """Save the document to the specified path."""
        try:
            self.document.save(output_path)
            logger.info(f"Document saved successfully to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise
    
    def create_summary_page(self, translation_stats: Dict):
        """Add a summary page with translation statistics."""
        # Add summary heading
        summary_heading = self.document.add_heading('Translation Summary', level=1)
        summary_heading.style = self.document.styles['CustomTitle']
        
        # Add summary table
        table = self.document.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        
        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Metric'
        header_cells[1].text = 'Value'
        
        # Style header row
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                paragraph.style = self.document.styles['CustomTableHeader']
        
        # Add statistics rows
        stats_data = [
            ('Total Chunks', str(translation_stats.get('total_chunks', 0))),
            ('Successful Translations', str(translation_stats.get('successful_translations', 0))),
            ('Failed Translations', str(translation_stats.get('failed_translations', 0))),
            ('Success Rate', f"{translation_stats.get('success_rate', 0):.1%}"),
            ('Total Original Characters', str(translation_stats.get('total_original_chars', 0))),
            ('Total Translated Characters', str(translation_stats.get('total_translated_chars', 0))),
            ('Average Expansion Ratio', f"{translation_stats.get('average_expansion_ratio', 0):.2f}")
        ]
        
        for metric, value in stats_data:
            row_cells = table.add_row().cells
            row_cells[0].text = metric
            row_cells[1].text = value
        
        # Add page break after summary
        self.document.add_page_break()

    def add_image_from_base64(self, base64_string: str, width: float = 4.0, height: float = 3.0,
                             caption: str = "", image_format: str = "PNG"):
        """
        Add an image to the document from a base64 encoded string.
        
        Args:
            base64_string (str): Base64 encoded image data
            width (float): Image width in inches (default: 4.0)
            height (float): Image height in inches (default: 3.0)
            caption (str): Optional caption below the image
            image_format (str): Image format (PNG, JPEG, etc.)
        
        Returns:
            bool: True if image was added successfully, False otherwise
        """
        try:
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            
            # Create PIL Image object to validate and potentially convert
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Save to BytesIO with specified format
            img_buffer = io.BytesIO()
            image.save(img_buffer, format=image_format)
            img_buffer.seek(0)
            
            # Add image to document
            paragraph = self.document.add_paragraph()
            run = paragraph.add_run()
            
            # Add the image to the run
            run.add_picture(img_buffer, width=Inches(width), height=Inches(height))
            
            # Add caption if provided
            if caption:
                caption_para = self.document.add_paragraph(caption)
                caption_para.style = self.document.styles['CustomNormal']
                caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add some spacing after the image
            self.document.add_paragraph("")
            
            logger.info(f"✅ Image added successfully: {width}x{height} inches, format: {image_format}")
            return True
            
        except base64.binascii.Error as e:
            logger.error(f"❌ Invalid base64 string: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to add image from base64: {e}")
            return False
    
    def add_image_from_base64_with_auto_size(self, base64_string: str, max_width: float = 6.0, 
                                           max_height: float = 8.0, caption: str = "", 
                                           image_format: str = "PNG"):
        """
        Add an image to the document from base64 with automatic sizing to fit within bounds.
        
        Args:
            base64_string (str): Base64 encoded image data
            max_width (float): Maximum width in inches (default: 6.0)
            max_height (float): Maximum height in inches (default: 8.0)
            caption (str): Optional caption below the image
            image_format (str): Image format (PNG, JPEG, etc.)
        
        Returns:
            bool: True if image was added successfully, False otherwise
        """
        try:
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            
            # Create PIL Image object to get dimensions
            image = Image.open(io.BytesIO(image_data))
            
            # Calculate aspect ratio and dimensions
            img_width, img_height = image.size
            aspect_ratio = img_width / img_height
            
            # Calculate dimensions to fit within bounds while maintaining aspect ratio
            if aspect_ratio > 1:  # Landscape
                width = min(max_width, img_width / 96)  # Convert pixels to inches (96 DPI)
                height = width / aspect_ratio
                if height > max_height:
                    height = max_height
                    width = height * aspect_ratio
            else:  # Portrait
                height = min(max_height, img_height / 96)
                width = height * aspect_ratio
                if width > max_width:
                    width = max_width
                    height = width / aspect_ratio
            
            # Use the main method to add the image
            return self.add_image_from_base64(
                base64_string, 
                width=width, 
                height=height, 
                caption=caption, 
                image_format=image_format
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to add image with auto-sizing: {e}")
            return False
