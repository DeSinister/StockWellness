#!/usr/bin/env python3
"""
Complete fix: Create matching chunks.json and embeddings.npy from clean local data
This fixes both the metadata AND the index mismatch
"""

import json
import numpy as np
import boto3
from sentence_transformers import SentenceTransformer
import os

def main():
    print("🔧 COMPLETE FIX: Creating matching chunks + embeddings...")
    
    # Load clean local data
    with open('extracted_books_final.json', 'r') as f:
        local_books = json.load(f)
    print(f"📚 Loaded {len(local_books)} clean chunks from local file")
    
    # Prepare data for Lambda
    chunks_for_lambda = []
    texts_for_embeddings = []
    
    for book in local_books:
        if book.get('text'):  # Only include non-empty text
            chunk = {
                'book': book.get('book_name', ''),
                'page': book.get('page_number', 0),
                'text': book.get('text', '')
            }
            chunks_for_lambda.append(chunk)
            texts_for_embeddings.append(book.get('text', ''))
    
    print(f"📊 Prepared {len(chunks_for_lambda)} chunks and {len(texts_for_embeddings)} texts")
    
    # Show sample
    if chunks_for_lambda:
        sample = chunks_for_lambda[0]
        print(f"📖 Sample: '{sample['book']}' page {sample['page']}")
        print(f"📝 Text: {sample['text'][:100]}...")
    
    # Load sentence transformer and create embeddings
    print("🤖 Loading sentence transformer...")
    model = SentenceTransformer('all-mpnet-base-v2')
    
    print("🧠 Computing embeddings for all chunks...")
    embeddings = model.encode(texts_for_embeddings, convert_to_tensor=False, show_progress_bar=True)
    print(f"✅ Created embeddings with shape: {embeddings.shape}")
    
    # Save locally first
    print("💾 Saving files...")
    with open('chunks_complete.json', 'w') as f:
        json.dump(chunks_for_lambda, f, indent=2)
    
    np.save('embeddings_complete.npy', embeddings)
    
    # Upload to S3
    print("☁️ Uploading MATCHING files to S3...")
    s3 = boto3.client('s3')
    
    # Upload chunks
    s3.upload_file('chunks_complete.json', 'stockwellness-models', 'rag/chunks.json')
    print("✅ Uploaded chunks.json")
    
    # Upload embeddings  
    s3.upload_file('embeddings_complete.npy', 'stockwellness-models', 'rag/embeddings.npy')
    print("✅ Uploaded embeddings.npy")
    
    # Cleanup
    os.remove('chunks_complete.json')
    os.remove('embeddings_complete.npy')
    
    print("🎉 COMPLETE FIX DONE!")
    print(f"📊 Both files now have exactly {len(chunks_for_lambda)} items")
    print("✅ Book names and page numbers will show correctly")
    print("✅ No more index mismatch errors")
    print("🧪 Wait 2-3 minutes for Lambda to pick up new files, then test!")

if __name__ == "__main__":
    main() 