#!/usr/bin/env python3
"""
Example script demonstrating PDF splitting functionality.
"""

import os
import sys
from pdf_utils import PDFSplitter


def demonstrate_page_range_splitting():
    """Demonstrate creating PDFs with specific page ranges."""
    
    print("\n" + "=" * 60)
    print("🎯 PAGE RANGE PDF CREATION DEMONSTRATION")
    print("=" * 60)
    
    # Example PDF paths (you would need to provide actual PDFs)
    example_pdfs = ["Chapter9.pdf"]
    
    # Check which example PDFs exist
    available_pdfs = [pdf for pdf in example_pdfs if os.path.exists(pdf)]
    
    if not available_pdfs:
        print("⚠️  No example PDFs found. Skipping page range demo.")
        return
    
    print(f"📚 Found {len(available_pdfs)} example PDF(s): {', '.join(available_pdfs)}")
    
    try:
        splitter = PDFSplitter()
        
        # Demonstrate page range splitting
        print("\n🎯 Creating PDF with pages 1-6...")
        first_pdf = available_pdfs[0]
        
        # Create PDF with pages 1-6 (0-indexed, so pages 1-6)
        range_output_dir = "page_range1"
        output_file = splitter.split_pdf_by_pages(
            first_pdf, 
            range_output_dir, 
            "range_page", 
            start_page=0,  # 0-indexed (page 1)
            end_page=3     # 0-indexed (page 6)
        )
        print(f"✅ PDF created with pages 1-6: {os.path.basename(output_file)}")

    except Exception as e:
        print(f"❌ Page range demo failed: {e}")


if __name__ == "__main__":
    # main()
    
    # Uncomment the line below to run page range splitting demonstration
    demonstrate_page_range_splitting()
