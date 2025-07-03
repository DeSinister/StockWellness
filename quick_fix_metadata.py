#!/usr/bin/env python3
"""
Quick fix: Upload local book data to S3 with correct field names
This fixes the missing book names and page numbers issue
"""

import json
import boto3

def main():
    print("🔧 Quick fix for metadata structure...")
    
    # Load the local data with proper book names/pages
    with open('extracted_books_final.json', 'r') as f:
        local_books = json.load(f)
    print(f"📚 Loaded {len(local_books)} chunks from local file")
    
    # Convert to the format Lambda expects
    chunks_for_lambda = []
    for book in local_books:
        if book.get('text'):  # Only include non-empty text
            chunk = {
                'book': book.get('book_name', ''),      # Lambda expects 'book'
                'page': book.get('page_number', 0),     # Lambda expects 'page'
                'text': book.get('text', '')
            }
            chunks_for_lambda.append(chunk)
    
    print(f"📋 Converted {len(chunks_for_lambda)} chunks to Lambda format")
    
    # Show sample to verify
    if chunks_for_lambda:
        sample = chunks_for_lambda[0]
        print(f"📖 Sample: '{sample['book']}' page {sample['page']}")
    
    # Save and upload to S3
    with open('chunks_metadata_fixed.json', 'w') as f:
        json.dump(chunks_for_lambda, f, indent=2)
    
    # Upload to S3 (overwrite the broken chunks.json)
    s3 = boto3.client('s3')
    s3.upload_file('chunks_metadata_fixed.json', 'stockwellness-models', 'rag/chunks.json')
    
    print("✅ Uploaded fixed chunks.json with proper book names and page numbers!")
    print("🧪 Test your Lambda now - the metadata should appear!")
    
    # Cleanup
    import os
    os.remove('chunks_metadata_fixed.json')

if __name__ == "__main__":
    main() 