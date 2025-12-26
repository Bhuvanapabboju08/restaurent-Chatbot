"""
Flask REST API for RAG-based Restaurant Assistant
Provides endpoints for document upload, chat queries, and system management
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import traceback

# Import custom modules
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from vector_store import VectorStore
from groq_client import GroqClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
CORS(app, origins=allowed_origins.split(","))

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
app.config['UPLOAD_FOLDER'] = './data/documents'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services (singleton pattern)
doc_processor = DocumentProcessor(
    chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200))
)
embedding_service = EmbeddingService()
vector_store = VectorStore()
groq_client = GroqClient()

print("[OK] All services initialized successfully!")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "RAG Restaurant Assistant API is running",
        "services": {
            "document_processor": "ready",
            "embedding_service": "ready",
            "vector_store": "ready",
            "groq_client": "ready"
        }
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document
    
    Request:
        - file: Document file (PDF or DOCX)
    
    Response:
        - success: boolean
        - message: string
        - document_id: string
        - chunks_created: int
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(file_path)
        
        # Process document
        print(f"Processing document: {filename}")
        chunks, doc_hash = doc_processor.process_document(file_path, filename)
        
        # Check if document already exists
        if vector_store.document_exists(doc_hash):
            return jsonify({
                "success": True,
                "message": "Document already exists in database",
                "document_id": f"doc_{doc_hash[:8]}",
                "chunks_created": 0,
                "already_exists": True
            }), 200
        
        # Generate embeddings
        print(f"Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(
            chunk_texts,
            batch_size=32,
            show_progress=False
        )
        
        # Store in vector database
        document_id = f"doc_{doc_hash[:8]}"
        vector_store.add_documents(chunks, embeddings, document_id)
        
        print(f"[OK] Document processed successfully: {filename}")
        
        return jsonify({
            "success": True,
            "message": "Document uploaded and processed successfully",
            "document_id": document_id,
            "document_name": filename,
            "chunks_created": len(chunks),
            "already_exists": False
        }), 201
        
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Query the RAG system with a question
    
    Request:
        - question: string (required)
        - top_k: int (optional, default: 5)
        - temperature: float (optional, default: 0.7)
        - max_tokens: int (optional, default: 500)
    
    Response:
        - success: boolean
        - answer: string
        - sources: list of relevant chunks
        - tokens_used: object
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": "Question is required"
            }), 400
        
        question = data['question']
        top_k = data.get('top_k', 5)
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 500)
        
        # Validate question
        if not question.strip():
            return jsonify({
                "success": False,
                "error": "Question cannot be empty"
            }), 400
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(question)
        
        # Retrieve similar chunks
        results = vector_store.query_similar(query_embedding, top_k=top_k)
        
        # Check if any documents exist
        if results['count'] == 0:
            return jsonify({
                "success": True,
                "answer": "I don't have any documents to reference. Please upload some restaurant documents first.",
                "sources": [],
                "tokens_used": None
            }), 200
        
        # Prepare context from retrieved chunks
        context = "\n\n".join([r["text"] for r in results['results']])
        
        # Generate answer using LLM
        response = groq_client.chat_completion(
            user_question=question,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Format sources for frontend
        sources = [
            {
                "text": r["text"],
                "document_name": r["metadata"].get("document_name", "unknown"),
                "chunk_index": r["metadata"].get("chunk_index", 0),
                "similarity": round(r["similarity"], 3)
            }
            for r in results['results']
        ]
        
        return jsonify({
            "success": True,
            "answer": response['response'],
            "sources": sources,
            "tokens_used": response['tokens_used'],
            "model": response['model']
        }), 200
        
    except Exception as e:
        print(f"Error processing chat query: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """
    Get list of all documents in the vector store
    
    Response:
        - success: boolean
        - documents: list of document objects
        - total_documents: int
        - total_chunks: int
    """
    try:
        documents = vector_store.get_all_documents()
        stats = vector_store.get_stats()
        
        return jsonify({
            "success": True,
            "documents": documents,
            "total_documents": stats['total_documents'],
            "total_chunks": stats['total_chunks']
        }), 200
        
    except Exception as e:
        print(f"Error listing documents: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete a document from the vector store
    
    Parameters:
        - document_id: string (in URL path)
    
    Response:
        - success: boolean
        - message: string
        - chunks_deleted: int
    """
    try:
        chunks_deleted = vector_store.delete_document(document_id)
        
        if chunks_deleted > 0:
            return jsonify({
                "success": True,
                "message": f"Document deleted successfully",
                "document_id": document_id,
                "chunks_deleted": chunks_deleted
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Document not found"
            }), 404
            
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    Response:
        - success: boolean
        - stats: object with system information
    """
    try:
        stats = vector_store.get_stats()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_documents": stats['total_documents'],
                "total_chunks": stats['total_chunks'],
                "collection_name": stats['collection_name'],
                "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                "llm_model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                "chunk_size": int(os.getenv("CHUNK_SIZE", 1000)),
                "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", 200))
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def semantic_search():
    """
    Perform semantic search without LLM response
    
    Request:
        - query: string (required)
        - top_k: int (optional, default: 5)
    
    Response:
        - success: boolean
        - results: list of matching chunks with similarity scores
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        # Retrieve similar chunks
        results = vector_store.query_similar(query_embedding, top_k=top_k)
        
        # Format results
        formatted_results = [
            {
                "text": r["text"],
                "document_name": r["metadata"].get("document_name", "unknown"),
                "document_id": r["metadata"].get("document_id", "unknown"),
                "chunk_index": r["metadata"].get("chunk_index", 0),
                "similarity": round(r["similarity"], 3)
            }
            for r in results['results']
        ]
        
        return jsonify({
            "success": True,
            "query": query,
            "results": formatted_results,
            "count": results['count']
        }), 200
        
    except Exception as e:
        print(f"Error performing search: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        "success": False,
        "error": "File is too large. Maximum size is 10MB."
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print("\n" + "="*60)
    print("[APP] RAG Restaurant Assistant API")
    print("="*60)
    print(f"[OK] Server starting on http://localhost:{port}")
    print(f"[OK] Debug mode: {debug}")
    print(f"[OK] Allowed origins: {allowed_origins}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )