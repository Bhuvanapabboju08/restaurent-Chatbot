"""
Diagnostic script to identify initialization issues
"""

import os
import sys
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Load environment variables
load_dotenv()

print("=" * 70)
print("DIAGNOSTIC SCRIPT - Checking all services")
print("=" * 70)

# 1. Check environment variables
print("\n1. ENVIRONMENT VARIABLES:")
print("-" * 70)
env_vars = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL"),
    "GROQ_MODEL": os.getenv("GROQ_MODEL"),
    "CHROMA_PERSIST_DIR": os.getenv("CHROMA_PERSIST_DIR"),
}

for key, value in env_vars.items():
    if value:
        display = value[:20] + "..." if len(value) > 20 else value
        print(f"✓ {key}: {display}")
    else:
        print(f"✗ {key}: NOT SET")

# 2. Check required packages
print("\n2. REQUIRED PACKAGES:")
print("-" * 70)
required_packages = [
    "flask",
    "flask_cors",
    "openai",
    "groq",
    "chromadb",
    "PyPDF2",
    "python-docx",
    "numpy"
]

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - NOT INSTALLED")

# 3. Test DocumentProcessor
print("\n3. TESTING DocumentProcessor:")
print("-" * 70)
try:
    from document_processor import DocumentProcessor
    doc_processor = DocumentProcessor()
    print("✓ DocumentProcessor initialized successfully")
except Exception as e:
    print(f"✗ DocumentProcessor failed: {str(e)}")
    import traceback
    traceback.print_exc()

# 4. Test EmbeddingService
print("\n4. TESTING EmbeddingService:")
print("-" * 70)
try:
    from embedding_service import EmbeddingService
    embedding_service = EmbeddingService()
    print("✓ EmbeddingService initialized successfully")

    # Test a simple embedding
    test_embedding = embedding_service.generate_embedding("test query")
    print(f"✓ Test embedding generated: dimension {len(test_embedding)}")
except Exception as e:
    print(f"✗ EmbeddingService failed: {str(e)}")
    import traceback
    traceback.print_exc()

# 5. Test VectorStore
print("\n5. TESTING VectorStore:")
print("-" * 70)
try:
    from vector_store import VectorStore
    vector_store = VectorStore()
    print("✓ VectorStore initialized successfully")
    stats = vector_store.get_stats()
    print(f"✓ Current stats - Documents: {stats['total_documents']}, Chunks: {stats['total_chunks']}")
except Exception as e:
    print(f"✗ VectorStore failed: {str(e)}")
    import traceback
    traceback.print_exc()

# 6. Test GroqClient
print("\n6. TESTING GroqClient:")
print("-" * 70)
try:
    from groq_client import GroqClient
    groq_client = GroqClient()
    print("✓ GroqClient initialized successfully")

    # Test connection
    response = groq_client.chat_completion(
        user_question="Say 'working' if you receive this",
        max_tokens=10
    )
    print(f"✓ Test response received: {response['response'][:50]}")
except Exception as e:
    print(f"✗ GroqClient failed: {str(e)}")
    import traceback
    traceback.print_exc()

# 7. Check data directories
print("\n7. DATA DIRECTORIES:")
print("-" * 70)
directories = [
    "./data/documents",
    "./data/chroma_db"
]

for directory in directories:
    if os.path.exists(directory):
        file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        print(f"✓ {directory} exists - {file_count} files")
    else:
        print(f"⚠ {directory} does not exist")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
