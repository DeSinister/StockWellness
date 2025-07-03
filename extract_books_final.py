#!/usr/bin/env python3
"""
Final book extraction with multiple methods to handle difficult PDFs
"""

import os
import re
from pathlib import Path
import json
import hashlib
import logging
from typing import List, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_readable_text(text: str) -> bool:
    """Check if text is readable English"""
    if not text or len(text) < 10:
        return False
    
    # Count readable English words
    words = text.split()
    readable_words = 0
    
    common_words = {'the', 'and', 'or', 'to', 'of', 'in', 'a', 'is', 'that', 'for', 'with', 'on', 'by', 'this', 'be', 'as', 'from', 'are', 'was', 'at', 'an'}
    
    for word in words[:20]:  # Check first 20 words
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word in common_words or clean_word.isalpha() and len(clean_word) > 2:
            readable_words += 1
    
    # If at least 30% of words are readable, consider it good
    return readable_words / min(len(words), 20) > 0.3

def extract_with_different_methods(pdf_path: Path) -> List[Dict[str, Any]]:
    """Try multiple extraction methods for problematic PDFs"""
    if not fitz:
        return []
    
    pages_data = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(len(doc), 10)):  # Test first 10 pages
        page = doc[page_num]
        best_text = ""
        
        # Method 1: Default text extraction
        try:
            text1 = page.get_text()
            if is_readable_text(text1):
                best_text = text1
        except:
            pass
        
        # Method 2: Text with layout preservation
        if not best_text:
            try:
                text2 = page.get_text("text")
                if is_readable_text(text2):
                    best_text = text2
            except:
                pass
        
        # Method 3: Dictionary-based extraction
        if not best_text:
            try:
                text_dict = page.get_text("dict")
                extracted_text = ""
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                extracted_text += span.get("text", "") + " "
                if is_readable_text(extracted_text):
                    best_text = extracted_text
            except:
                pass
        
        # Method 4: OCR-like extraction using image conversion (if text is garbled)
        if not best_text:
            try:
                # This requires additional setup but can help with difficult PDFs
                logger.debug(f"All text extraction methods failed for page {page_num + 1}")
            except:
                pass
        
        if best_text:
            # Clean the text
            clean_text = re.sub(r'\s+', ' ', best_text).strip()
            if len(clean_text) > 50:
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': clean_text,
                    'book_name': pdf_path.stem,
                    'file_path': str(pdf_path)
                })
    
    doc.close()
    return pages_data

def try_pypdf2_extraction(pdf_path: Path) -> List[Dict[str, Any]]:
    """Try PyPDF2 as alternative extraction method"""
    if not PyPDF2:
        return []
    
    pages_data = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages[:10]):  # Test first 10 pages
                try:
                    text = page.extract_text()
                    if is_readable_text(text):
                        clean_text = re.sub(r'\s+', ' ', text).strip()
                        if len(clean_text) > 50:
                            pages_data.append({
                                'page_number': page_num + 1,
                                'text': clean_text,
                                'book_name': pdf_path.stem,
                                'file_path': str(pdf_path)
                            })
                except:
                    continue
    except:
        pass
    
    return pages_data

def extract_books_with_validation(books_dir="Books", output_file="extracted_books_final.json"):
    """Extract books with validation of text quality"""
    books_dir = Path(books_dir)
    
    if not books_dir.exists():
        logger.error(f"Books directory {books_dir} does not exist")
        return
    
    pdf_files = list(books_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {books_dir}")
        return
    
    all_chunks = []
    
    for pdf_path in pdf_files:
        logger.info(f"Processing {pdf_path.name}...")
        
        # Try PyMuPDF first
        pages_data = extract_with_different_methods(pdf_path)
        
        # If PyMuPDF didn't work well, try PyPDF2
        if not pages_data or len(pages_data) < 5:
            logger.info(f"Trying alternative extraction for {pdf_path.name}")
            pages_data = try_pypdf2_extraction(pdf_path)
        
        if not pages_data:
            logger.warning(f"Could not extract readable text from {pdf_path.name}")
            logger.info(f"This PDF might need manual processing or OCR")
            continue
        
        # Create chunks
        for page_data in pages_data:
            text = page_data['text']
            word_count = len(text.split())
            
            chunk = {
                'id': hashlib.md5(f"{page_data['book_name']}_page_{page_data['page_number']}".encode()).hexdigest(),
                'text': text,
                'book_name': page_data['book_name'],
                'page_number': page_data['page_number'],
                'file_path': page_data['file_path'],
                'word_count': word_count
            }
            all_chunks.append(chunk)
        
        logger.info(f"Extracted {len(pages_data)} readable pages from {pdf_path.name}")
        
        # Show sample
        if pages_data:
            sample_text = pages_data[0]['text'][:200]
            logger.info(f"Sample: {sample_text}...")
    
    if not all_chunks:
        print("\n❌ No readable text could be extracted from any books.")
        print("This could be due to:")
        print("1. PDFs with image-based text (need OCR)")
        print("2. Protected/encrypted PDFs")
        print("3. PDFs with unusual font encoding")
        print("\nSuggestion: Try converting PDFs to text format first, or use different PDF files.")
        return
    
    # Save to JSON
    output_path = Path(output_file)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    avg_words = sum(chunk['word_count'] for chunk in all_chunks) / len(all_chunks)
    
    print(f"\n✅ Extraction Complete!")
    print(f"📚 Successfully processed {len(set(chunk['book_name'] for chunk in all_chunks))} books")
    print(f"📄 Extracted {len(all_chunks)} readable chunks")
    print(f"💾 Saved to {output_file} ({file_size_mb:.1f} MB)")
    print(f"📝 Average words per chunk: {avg_words:.0f}")

if __name__ == "__main__":
    extract_books_with_validation() 