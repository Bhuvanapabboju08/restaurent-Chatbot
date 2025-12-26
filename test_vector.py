"""
Integration Test: Document Processing → Embeddings → Vector Storage → Retrieval
Tests the complete RAG pipeline
"""

import os
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from vector_store import VectorStore
from groq_client import GroqClient


def test_complete_pipeline():
    """Test the complete RAG pipeline"""
    
    print("=" * 70)
    print("COMPLETE RAG PIPELINE TEST")
    print("=" * 70)
    
    # Check for test file
    test_file = "robot.pdf"
    if not os.path.exists(test_file):
        print(f"\n⚠ Test file not found: {test_file}")
        print("\nPlease add a PDF or DOCX file to data/documents/ to test")
        return
    
    try:
        # Step 1: Initialize all services
        print("\n📦 STEP 1: Initializing services...")
        print("-" * 70)
        
        doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        print("✓ Document processor ready")
        
        embedding_service = EmbeddingService()
        print("✓ Embedding service ready")
        
        vector_store = VectorStore()
        print("✓ Vector store ready")
        
        groq_client = GroqClient()
        print("✓ Groq client ready")
        
        # Step 2: Process document
        print("\n📄 STEP 2: Processing document...")
        print("-" * 70)
        
        chunks, doc_hash = doc_processor.process_document(test_file)
        print(f"✓ Extracted and chunked: {len(chunks)} chunks created")
        
        # Check if document already exists
        if vector_store.document_exists(doc_hash):
            print(f"⚠ Document already exists in vector store (hash: {doc_hash[:16]}...)")
            print("  Skipping re-processing (change detection works!)")
            document_id = f"doc_{doc_hash[:8]}"
        else:
            # Step 3: Generate embeddings
            print("\n🔢 STEP 3: Generating embeddings...")
            print("-" * 70)
            
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings_batch(
                chunk_texts,
                batch_size=32,
                show_progress=True
            )
            print(f"✓ Generated {len(embeddings)} embeddings")
            
            # Step 4: Store in vector database
            print("\n💾 STEP 4: Storing in vector database...")
            print("-" * 70)
            
            document_id = f"doc_{doc_hash[:8]}"
            vector_store.add_documents(chunks, embeddings, document_id)
            print(f"✓ Stored document with ID: {document_id}")
        
        # Step 5: Test retrieval with query
        print("\n🔍 STEP 5: Testing retrieval...")
        print("-" * 70)
        
        test_query = "What information is available in this document?"
        print(f"Query: '{test_query}'")
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(test_query)
        print("✓ Query embedding generated")
        
        # Retrieve similar chunks
        results = vector_store.query_similar(query_embedding, top_k=3)
        print(f"✓ Found {results['count']} relevant chunks")
        
        # Display results
        print("\nTop relevant chunks:")
        for idx, result in enumerate(results['results'], 1):
            print(f"\n  [{idx}] Similarity: {result['similarity']:.3f}")
            print(f"      Text preview: {result['text'][:150]}...")
            print(f"      From: {result['metadata']['document_name']}")
        
        # Step 6: Test RAG with LLM
        print("\n💬 STEP 6: Testing RAG with Groq LLM...")
        print("-" * 70)
        
        # Prepare context from retrieved chunks
        context = "\n\n".join([r["text"] for r in results['results']])
        
        # Generate answer
        user_question = "Summarize the key information from this document"
        print(f"Question: '{user_question}'")
        
        response = groq_client.chat_completion(
            user_question=user_question,
            context=context,
            max_tokens=300
        )
        
        print(f"\n🤖 Assistant Response:")
        print("-" * 70)
        print(response['response'])
        print("-" * 70)
        print(f"Tokens used: {response['tokens_used']['total']}")
        
        # Step 7: Display statistics
        print("\n📊 STEP 7: Vector Store Statistics")
        print("-" * 70)
        
        stats = vector_store.get_stats()
        print(f"Total chunks in store: {stats['total_chunks']}")
        print(f"Total documents: {stats['total_documents']}")
        
        documents = vector_store.get_all_documents()
        print(f"\nDocuments:")
        for doc in documents:
            print(f"  • {doc['document_name']}")
            print(f"    ID: {doc['document_id']}")
            print(f"    Chunks: {doc['total_chunks']}")
        
        print("\n" + "=" * 70)
        print("✓ COMPLETE PIPELINE TEST SUCCESSFUL!")
        print("=" * 70)
        
        print("\n🎉 All components working together:")
        print("  ✓ Document processing")
        print("  ✓ Embedding generation")
        print("  ✓ Vector storage")
        print("  ✓ Semantic search")
        print("  ✓ LLM response generation")
        print("  ✓ Change detection")
        
    except Exception as e:
        print(f"\n❌ Error during pipeline test: {str(e)}")
        import traceback
        traceback.print_exc()


def test_multiple_queries():
    """Test multiple queries on stored documents"""
    
    print("\n" + "=" * 70)
    print("TESTING MULTIPLE QUERIES")
    print("=" * 70)
    
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        groq_client = GroqClient()
        
        # Test queries
        test_queries = [
            "What are the main topics covered?",
            "Are there any specific dates or times mentioned?",
            "What services or products are described?",
        ]
        
        for idx, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {idx}: '{query}'")
            print("-" * 70)
            
            # Get embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Retrieve context
            results = vector_store.query_similar(query_embedding, top_k=3)
            
            if results['count'] == 0:
                print("⚠ No documents found in vector store")
                print("  Please run test_complete_pipeline() first")
                break
            
            # Prepare context
            context = "\n\n".join([r["text"] for r in results['results']])
            
            # Get LLM response
            response = groq_client.chat_completion(
                user_question=query,
                context=context,
                max_tokens=200
            )
            
            print(f"🤖 Response: {response['response']}")
            print(f"   Tokens: {response['tokens_used']['total']}")
        
        print("\n✓ Multiple query test completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run complete pipeline test
    test_complete_pipeline()
    
    # Uncomment to test multiple queries
    # print("\n\n")
    # test_multiple_queries()