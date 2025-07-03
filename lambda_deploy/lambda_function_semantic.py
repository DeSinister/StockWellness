import json
import boto3
import numpy as np
from sentence_transformers import SentenceTransformer
import tempfile
import os
import shutil
from sklearn.metrics.pairwise import cosine_similarity

# Global variables for caching
model = None
book_embeddings = None
book_chunks = None

def get_model():
    """Load the sentence transformer model (cached globally)"""
    global model
    if model is None:
        print("🤖 Loading sentence transformer model...")
        model = SentenceTransformer('all-mpnet-base-v2')
        print("✅ Model loaded and cached!")
    return model

def load_precomputed_data():
    """Load precomputed embeddings and chunks from S3 (cached globally)"""
    global book_embeddings, book_chunks
    
    if book_embeddings is not None and book_chunks is not None:
        print("📊 Using cached embeddings and chunks")
        return book_embeddings, book_chunks
    
    print("📥 Loading precomputed data from S3...")
    
    # Get bucket name from environment variable
    bucket_name = os.environ.get('S3_BUCKET_NAME', 'stockwellness-models')
    s3 = boto3.client('s3')
    
    # Create temporary files
    embeddings_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.npy')
    chunks_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    
    try:
        # Download precomputed embeddings
        print("📦 Downloading embeddings.npy...")
        s3.download_file(bucket_name, 'rag/embeddings.npy', embeddings_temp.name)
        book_embeddings = np.load(embeddings_temp.name)
        print(f"✅ Loaded embeddings with shape: {book_embeddings.shape}")
        
        # Download chunks data
        print("📚 Downloading chunks.json...")
        s3.download_file(bucket_name, 'rag/chunks.json', chunks_temp.name)
        with open(chunks_temp.name, 'r') as f:
            book_chunks = json.load(f)
        print(f"✅ Loaded {len(book_chunks)} book chunks")
        
        return book_embeddings, book_chunks
        
    finally:
        # Clean up temporary files
        try:
            os.unlink(embeddings_temp.name)
            os.unlink(chunks_temp.name)
        except:
            pass

def cleanup_tmp():
    """Clean up /tmp directory to avoid space issues"""
    try:
        tmp_dir = '/tmp'
        for item in os.listdir(tmp_dir):
            item_path = os.path.join(tmp_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except:
                continue  # Skip files we can't delete
        print("🧹 Cleaned up /tmp directory")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def lambda_handler(event, context):
    """
    AWS Lambda handler for semantic search using precomputed embeddings
    """
    try:
        print("🚀 Starting semantic search with precomputed embeddings...")
        
        # Clean up /tmp first
        cleanup_tmp()
        
        # Get query from event
        if 'body' in event:
            body = json.loads(event['body'])
            query = body.get('query', '')
        else:
            query = event.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'error': 'No query provided'})
            }
        
        print(f"🔍 Query: {query}")
        
        # Load model and precomputed data
        model = get_model()
        embeddings, chunks = load_precomputed_data()
        
        # Encode only the query (super fast!)
        print("🧠 Encoding query...")
        query_embedding = model.encode([query], convert_to_tensor=False)
        
        # Calculate similarities with precomputed embeddings
        print("📊 Calculating similarities...")
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        # Get top results
        top_k = 5
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            chunk = chunks[idx]
            similarity = float(similarities[idx])
            
            result = {
                'rank': i + 1,
                'similarity': similarity,
                'book_name': chunk.get('book', ''),
                'page': chunk.get('page', 0),
                'text': chunk.get('text', '')[:500] + ('...' if len(chunk.get('text', '')) > 500 else '')
            }
            results.append(result)
            print(f"📖 Result {i+1}: {similarity:.3f} - {chunk.get('book', '')} (page {chunk.get('page', 0)})")
        
        print("✅ Search completed successfully!")
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'query': query,
                'results': results,
                'total_chunks': len(chunks),
                'search_time': 'Fast with precomputed embeddings! ⚡'
            })
        }
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'error': str(e)})
        } 