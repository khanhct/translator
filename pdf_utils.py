import logging
import os
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFSplitter:
    """Utility class for splitting PDF files page by page."""
    
    def __init__(self):
        """Initialize PDF splitter with available PDF libraries."""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check which PDF libraries are available."""
        if PYPDF2_AVAILABLE:
            logger.info("✅ PyPDF2 is available for PDF operations")
        else:
            logger.warning("⚠️ PyPDF2 not available")
        
        if PYMUPDF_AVAILABLE:
            logger.info("✅ PyMuPDF (fitz) is available for PDF operations")
        else:
            logger.warning("⚠️ PyMuPDF not available")
    
    def split_pdf_by_pages(self, input_path: str, output_dir: str = None, 
                           output_prefix: str = "page", start_page: int = None,
                           end_page: int = None) -> str:
        """
        Create a PDF file containing pages from start_page to end_page.
        
        Args:
            input_path (str): Path to the input PDF file
            output_dir (str): Directory to save the output PDF (default: same as input)
            output_prefix (str): Prefix for output filename (default: "page")
            start_page (int): Starting page number (0-indexed, default: 0)
            end_page (int): Ending page number (0-indexed, default: last page)
        
        Returns:
            str: Path to the created PDF file containing the specified pages
        
        Raises:
            FileNotFoundError: If input PDF doesn't exist
            ValueError: If page range is invalid
            RuntimeError: If PDF processing fails
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input PDF file not found: {input_path}")
        
        # Set default output directory
        if output_dir is None:
            output_dir = os.path.dirname(input_path) or "."
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get input file info
        input_file = Path(input_path)
        input_name = input_file.stem
        
        try:
            if PYPDF2_AVAILABLE:
                return self._split_with_pypdf2(input_path, output_dir, output_prefix, start_page, end_page, input_name)
            elif PYMUPDF_AVAILABLE:
                return self._split_with_pymupdf(input_path, output_dir, output_prefix, start_page, end_page, input_name)
            else:
                raise RuntimeError("No PDF library available. Install PyPDF2 or PyMuPDF.")
                
        except Exception as e:
            logger.error(f"Failed to split PDF: {e}")
            raise RuntimeError(f"PDF splitting failed: {e}")
    
    def _split_with_pypdf2(self, input_path: str, output_dir: str, output_prefix: str,
                           start_page: int, end_page: int, input_name: str) -> str:
        """Create PDF with pages from start_page to end_page using PyPDF2 library."""
        logger.info(f"Creating PDF with pages {start_page + 1}-{end_page + 1} using PyPDF2: {input_path}")
        
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            
            # Validate page range
            start_page = start_page or 0
            end_page = end_page or total_pages - 1
            
            if not (0 <= start_page <= end_page < total_pages):
                raise ValueError(f"Invalid page range: {start_page}-{end_page} (total: {total_pages})")
            
            # Create PDF writer
            writer = PdfWriter()
            
            # Add pages from start_page to end_page
            for page_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[page_num])
            
            # Generate output filename
            output_filename = f"{output_prefix}_{start_page + 1:03d}_to_{end_page + 1:03d}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Write PDF to file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            logger.info(f"✅ PDF created with pages {start_page + 1}-{end_page + 1}: {output_filename}")
            return output_path
    
    def _split_with_pymupdf(self, input_path: str, output_dir: str, output_prefix: str,
                            start_page: int, end_page: int, input_name: str) -> str:
        """Create PDF with pages from start_page to end_page using PyMuPDF library."""
        logger.info(f"Creating PDF with pages {start_page + 1}-{end_page + 1} using PyMuPDF: {input_path}")
        
        doc = fitz.open(input_path)
        total_pages = len(doc)
        
        # Validate page range
        start_page = start_page or 0
        end_page = end_page or total_pages - 1
        
        if not (0 <= start_page <= end_page < total_pages):
            raise ValueError(f"Invalid page range: {start_page}-{end_page} (total: {total_pages})")
        
        # Create new document with specified pages
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        
        # Generate output filename
        output_filename = f"{output_prefix}_{start_page + 1:03d}_to_{end_page + 1:03d}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save PDF to file
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        logger.info(f"✅ PDF created with pages {start_page + 1}-{end_page + 1}: {output_filename}")
        return output_path
