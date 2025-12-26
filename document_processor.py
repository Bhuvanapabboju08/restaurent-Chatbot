"""
Document Processing Module
Handles PDF/DOCX extraction, text chunking, and document hashing
"""

import os
import hashlib
import re
from typing import List, Dict, Tuple
from pathlib import Path

import PyPDF2
from docx import Document

# Try to import alternative PDF libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class DocumentProcessor:
    """Process and chunk documents for RAG system"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods

        Tries in order:
        1. PyPDF2 (fast, works for most text-based PDFs)
        2. pdfplumber (better for complex layouts)
        3. OCR with pytesseract (for scanned/image PDFs)
        """
        text = ""

        # Method 1: Try PyPDF2 first (fastest)
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {page_num + 1}]\n{page_text}"

            if text.strip():
                print(f"✓ Extracted text using PyPDF2")
                return text
        except Exception as e:
            print(f"⚠ PyPDF2 failed: {str(e)}")

        # Method 2: Try pdfplumber (better for complex PDFs)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n[Page {page_num + 1}]\n{page_text}"

                if text.strip():
                    print(f"✓ Extracted text using pdfplumber")
                    return text
            except Exception as e:
                print(f"⚠ pdfplumber failed: {str(e)}")

        # Method 3: Try OCR for scanned PDFs (slowest but works for images)
        if OCR_AVAILABLE:
            try:
                print("Attempting OCR extraction (this may take a while)...")
                images = convert_from_path(file_path)

                for page_num, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image)
                    if page_text.strip():
                        text += f"\n[Page {page_num + 1}]\n{page_text}"

                if text.strip():
                    print(f"✓ Extracted text using OCR")
                    return text
            except Exception as e:
                print(f"⚠ OCR failed: {str(e)}")

        # If all methods fail
        error_msg = "No text could be extracted from PDF. "
        if not PDFPLUMBER_AVAILABLE and not OCR_AVAILABLE:
            error_msg += "\n\nInstall additional libraries for better PDF support:"
            error_msg += "\n  pip install pdfplumber"
            error_msg += "\n  pip install pdf2image pytesseract"
            error_msg += "\n\nFor OCR, also install Tesseract: https://github.com/tesseract-ocr/tesseract"

        raise ValueError(error_msg)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            if not text.strip():
                raise ValueError("No text could be extracted from DOCX")
                
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to include with each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split into sentences for smarter chunking
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                # Keep last few sentences for context
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += " " + sentence
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Create chunk objects with metadata
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks):
            chunk_obj = {
                "text": chunk_text,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "char_count": len(chunk_text)
            }
            
            # Add custom metadata if provided
            if metadata:
                chunk_obj.update(metadata)
                
            chunk_objects.append(chunk_obj)
        
        return chunk_objects
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\[\]{}\'\"]+', '', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be enhanced with NLTK/spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, chunk: str) -> str:
        """Get overlap text from end of chunk"""
        if len(chunk) <= self.chunk_overlap:
            return chunk
        
        # Try to get complete sentences for overlap
        overlap_start = len(chunk) - self.chunk_overlap
        sentences = self._split_into_sentences(chunk[overlap_start:])
        
        return " ".join(sentences)
    
    def generate_document_hash(self, file_path: str) -> str:
        """
        Generate MD5 hash of document for change detection
        
        Args:
            file_path: Path to document
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                
        return hash_md5.hexdigest()
    
    def process_document(self, file_path: str, document_name: str = None) -> Tuple[List[Dict], str]:
        """
        Complete document processing pipeline
        
        Args:
            file_path: Path to document
            document_name: Optional custom name (defaults to filename)
            
        Returns:
            Tuple of (chunk_list, document_hash)
        """
        # Extract text
        print(f"Extracting text from {file_path}...")
        text = self.extract_text(file_path)
        
        # Generate hash
        doc_hash = self.generate_document_hash(file_path)
        
        # Prepare metadata
        if document_name is None:
            document_name = Path(file_path).name
        
        metadata = {
            "document_name": document_name,
            "document_hash": doc_hash,
            "file_path": file_path
        }
        
        # Chunk text
        print(f"Chunking document into segments...")
        chunks = self.chunk_text(text, metadata)
        
        print(f"✓ Processed {document_name}: {len(chunks)} chunks created")
        
        return chunks, doc_hash


# Example usage and testing
if __name__ == "__main__":
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    
    # Test with a sample file (replace with your actual file path)
    test_file = "data/documents/sample.pdf"
    
    if os.path.exists(test_file):
        try:
            chunks, doc_hash = processor.process_document(test_file)
            
            print(f"\nDocument Hash: {doc_hash}")
            print(f"Total Chunks: {len(chunks)}")
            print(f"\nFirst chunk preview:")
            print(chunks[0]["text"][:200] + "...")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test file not found: {test_file}")
        print("Please add a PDF or DOCX file to data/documents/ for testing")