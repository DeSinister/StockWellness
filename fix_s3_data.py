#!/usr/bin/env python3
"""
URGENT FIX: Upload correct book data and embeddings to S3
The current S3 data is corrupted - this will fix it!
"""

import json
import numpy as np
import boto3
from sentence_transformers import SentenceTransformer
import os

def main():
    print("🚨 FIXING CORRUPTED S3 DATA...")
    
    # Load the GOOD local data
    print("📚 Loading clean book data...")
    with open('extracted_books_final.json', 'r') as f:
        books = json.load(f)
    print(f"✅ Loaded {len(books)} book chunks from CLEAN local file")
    
    # Load the sentence transformer model
    print("🤖 Loading sentence transformer model...")
    model = SentenceTransformer('all-mpnet-base-v2')
    print("✅ Model loaded!")
    
    # Prepare data in the format Lambda expects
    chunks = []
    texts = []
    
    for book in books:
        text = book.get('text', '')
        if text:  # Only include non-empty texts
            chunk = {
                'book': book.get('book_name', ''),  # Lambda expects 'book'
                'page': book.get('page_number', 0),  # Lambda expects 'page'  
                'text': text
            }
            chunks.append(chunk)
            texts.append(text)
    
    print(f"📊 Prepared {len(texts)} text chunks with proper book names and pages")
    
    # Show sample to verify
    if chunks:
        print(f"📖 Sample chunk: '{chunks[0]['book']}' page {chunks[0]['page']}")
        print(f"📝 Text preview: {chunks[0]['text'][:100]}...")
    
    # Compute embeddings
    print("🧠 Computing embeddings...")
    embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
    print(f"✅ Computed embeddings with shape: {embeddings.shape}")
    
    # Save to local files
    print("💾 Saving corrected data...")
    np.save('embeddings_fixed.npy', embeddings)
    with open('chunks_fixed.json', 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print("☁️ Uploading CORRECTED data to S3...")
    
    # Upload to S3 (overwrite the corrupted data)
    s3 = boto3.client('s3')
    
    # Upload corrected embeddings
    s3.upload_file('embeddings_fixed.npy', 'stockwellness-models', 'rag/embeddings.npy')
    print("✅ Uploaded corrected embeddings.npy")
    
    # Upload corrected chunks
    s3.upload_file('chunks_fixed.json', 'stockwellness-models', 'rag/chunks.json')
    print("✅ Uploaded corrected chunks.json")
    
    # Cleanup local files
    os.remove('embeddings_fixed.npy')
    os.remove('chunks_fixed.json')
    
    print("🎉 S3 DATA FIXED!")
    print("📍 Corrected files uploaded:")
    print("   - s3://stockwellness-models/rag/embeddings.npy")
    print("   - s3://stockwellness-models/rag/chunks.json")
    print("✅ Lambda will now return proper book names and page numbers!")

if __name__ == "__main__":
    main() 