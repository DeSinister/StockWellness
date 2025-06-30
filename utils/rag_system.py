import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    SentenceTransformer = None
    np = None
    cosine_similarity = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookRAGSystem:
    def __init__(self, books_dir: str = "Books", cache_dir: str = "cache/rag"):
        self.books_dir = Path(books_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunks_db = []
        self.embeddings = None
        
        # Initialize embedding model
        self.embedder = None
        if SentenceTransformer:
            try:
                self.embedder = SentenceTransformer('all-mpnet-base-v2')  # High quality 420MB model
                logger.info("Initialized SentenceTransformer embedding model")
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}")
        
        # Load or create chunks database
        self.load_or_create_database()
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page-level chunking"""
        pages_data = []
        
        try:
            if fitz:  # Use PyMuPDF if available
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    if text.strip():
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': text.strip(),
                            'book_name': pdf_path.stem,
                            'file_path': str(pdf_path)
                        })
                doc.close()
                
            elif PyPDF2:  # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        
                        if text.strip():
                            pages_data.append({
                                'page_number': page_num + 1,
                                'text': text.strip(),
                                'book_name': pdf_path.stem,
                                'file_path': str(pdf_path)
                            })
            else:
                logger.error("No PDF processing library available")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return []
        
        logger.info(f"Extracted {len(pages_data)} pages from {pdf_path.name}")
        return pages_data
    
    def detect_chapters(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect chapter boundaries and add chapter metadata"""
        current_chapter = "Introduction"
        chapter_patterns = [
            r'^CHAPTER\s+\d+',
            r'^Chapter\s+\d+',
            r'^\d+\.\s+[A-Z][^.]*$',
            r'^PART\s+[IVX]+',
        ]
        
        for page_data in pages_data:
            text_lines = page_data['text'].split('\n')
            
            # Check first few lines for chapter indicators
            for line in text_lines[:5]:
                line = line.strip()
                if len(line) > 3 and len(line) < 100:
                    for pattern in chapter_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            current_chapter = line
                            break
            
            page_data['chapter'] = current_chapter
        
        return pages_data
    
    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create searchable chunks with metadata"""
        chunks = []
        
        for page_data in pages_data:
            text = page_data['text']
            
            # Skip very short pages
            if len(text.strip()) < 100:
                continue
            
            # Create chunk with metadata
            chunk = {
                'id': hashlib.md5(f"{page_data['book_name']}_page_{page_data['page_number']}".encode()).hexdigest(),
                'text': text,
                'book_name': page_data['book_name'],
                'chapter': page_data.get('chapter', 'Unknown'),
                'page_number': page_data['page_number'],
                'file_path': page_data['file_path'],
                'word_count': len(text.split())
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def process_all_books(self) -> List[Dict[str, Any]]:
        """Process all PDF books"""
        all_chunks = []
        
        if not self.books_dir.exists():
            logger.error(f"Books directory {self.books_dir} does not exist")
            return []
        
        pdf_files = list(self.books_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            logger.info(f"Processing {pdf_path.name}...")
            
            pages_data = self.extract_text_from_pdf(pdf_path)
            if not pages_data:
                continue
            
            pages_data = self.detect_chapters(pages_data)
            book_chunks = self.create_chunks(pages_data)
            all_chunks.extend(book_chunks)
            
            logger.info(f"Created {len(book_chunks)} chunks from {pdf_path.name}")
        
        return all_chunks
    
    def compute_embeddings(self, chunks: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        """Compute embeddings for all chunks"""
        if not self.embedder or not chunks or not np:
            logger.warning("Cannot compute embeddings - missing dependencies")
            return None
        
        try:
            texts = [chunk['text'] for chunk in chunks]
            logger.info(f"Computing embeddings for {len(chunks)} chunks...")
            embeddings = self.embedder.encode(texts, show_progress_bar=True, batch_size=32)
            logger.info(f"Successfully computed embeddings shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error computing embeddings: {e}")
            return None
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search using vector embeddings and cosine similarity"""
        if not self.embedder or self.embeddings is None or not cosine_similarity or not np:
            logger.warning("Semantic search not available - missing embeddings or dependencies")
            return self.keyword_search_fallback(query, top_k)
        
        try:
            # Encode query
            query_embedding = self.embedder.encode([query])
            
            # Compute similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.chunks_db):  # Safety check
                    chunk = self.chunks_db[idx].copy()
                    chunk['relevance_score'] = float(similarities[idx])
                    results.append(chunk)
            
            top_scores = [r['relevance_score'] for r in results[:3]]
            logger.info(f"Semantic search found {len(results)} results with top scores: {top_scores}")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self.keyword_search_fallback(query, top_k)
    
    def keyword_search_fallback(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fallback keyword search when semantic search is not available"""
        query_words = set(query.lower().split())
        results = []
        
        for chunk in self.chunks_db:
            text_words = set(chunk['text'].lower().split())
            common_words = query_words.intersection(text_words)
            
            if common_words:
                score = len(common_words) / len(query_words)
                results.append({
                    **chunk,
                    'relevance_score': score
                })
        
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def retrieve_relevant_content_by_theme(self, investment_themes: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant book content based on investment themes from current events"""
        
        # Use the investment themes summary as the search query
        results = self.semantic_search(investment_themes, top_k)
        
        logger.info(f"Retrieved {len(results)} relevant chunks for themes: {investment_themes[:50]}...")
        return results
    
    def format_context_for_llm(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved content for LLM prompt"""
        if not relevant_chunks:
            return "No relevant investment literature found."
        
        context = "Investment Literature Context:\n\n"
        
        for i, chunk in enumerate(relevant_chunks, 1):
            context += f"Reference {i}: {chunk['book_name']} - {chunk['chapter']} (Page {chunk['page_number']})\n"
            
            # Truncate long chunks
            text = chunk['text']
            if len(text) > 400:
                text = text[:400] + "..."
            
            context += f"{text}\n\n"
        
        return context
    
    def save_database(self, chunks: List[Dict[str, Any]], embeddings: Optional[np.ndarray] = None):
        """Save chunks and embeddings to cache"""
        try:
            # Save chunks
            chunks_file = self.cache_dir / "chunks.json"
            with open(chunks_file, 'w') as f:
                json.dump(chunks, f, indent=2)
            
            # Save embeddings if available
            if embeddings is not None and np:
                embeddings_file = self.cache_dir / "embeddings.npy"
                np.save(embeddings_file, embeddings)
                logger.info(f"Saved embeddings with shape {embeddings.shape}")
            
            logger.info(f"Saved {len(chunks)} chunks to cache")
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def load_database(self) -> bool:
        """Load chunks and embeddings from cache"""
        try:
            chunks_file = self.cache_dir / "chunks.json"
            embeddings_file = self.cache_dir / "embeddings.npy"
            
            if not chunks_file.exists():
                return False
            
            # Load chunks
            with open(chunks_file, 'r') as f:
                self.chunks_db = json.load(f)
            
            # Load embeddings if available
            if embeddings_file.exists() and np:
                self.embeddings = np.load(embeddings_file)
                logger.info(f"Loaded embeddings with shape {self.embeddings.shape}")
            else:
                logger.warning("No embeddings found in cache - will recompute")
            
            logger.info(f"Loaded {len(self.chunks_db)} chunks from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return False
    
    def load_or_create_database(self):
        """Load existing database or create new one"""
        if not self.load_database():
            logger.info("Creating new RAG database...")
            chunks = self.process_all_books()
            if chunks:
                self.chunks_db = chunks
                # Compute embeddings for semantic search
                self.embeddings = self.compute_embeddings(chunks)
                self.save_database(chunks, self.embeddings)
            else:
                logger.warning("No chunks created")
        else:
            # If we loaded chunks but no embeddings, compute them
            if self.chunks_db and self.embeddings is None and self.embedder:
                logger.info("Computing missing embeddings for existing chunks...")
                self.embeddings = self.compute_embeddings(self.chunks_db)
                if self.embeddings is not None:
                    self.save_database(self.chunks_db, self.embeddings) 