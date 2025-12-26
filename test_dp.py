"""
Test script for document processor
Run this to verify PDF extraction and chunking works correctly
"""

from document_processor import DocumentProcessor
import os


def test_document_processor():
    """Test the document processor with a sample file"""
    
    print("=" * 60)
    print("DOCUMENT PROCESSOR TEST")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    print("\n✓ Document processor initialized")
    print(f"  - Chunk size: 1000 characters")
    print(f"  - Overlap: 200 characters")
    
    # Check for test file
    test_file = "robot.pdf"
    
    if not os.path.exists(test_file):
        print(f"\n⚠ No test file found at: {test_file}")
        print("\nTo test the processor:")
        print("1. Create 'data/documents/' folder if it doesn't exist")
        print("2. Add a PDF or DOCX file named 'sample.pdf' or 'sample.docx'")
        print("3. Run this script again")
        return
    
    try:
        # Process document
        print(f"\n📄 Processing: {test_file}")
        chunks, doc_hash = processor.process_document(test_file)
        
        # Display results
        print("\n" + "=" * 60)
        print("PROCESSING RESULTS")
        print("=" * 60)
        print(f"✓ Document hash: {doc_hash}")
        print(f"✓ Total chunks created: {len(chunks)}")
        
        # Show first chunk details
        print("\n" + "-" * 60)
        print("FIRST CHUNK DETAILS:")
        print("-" * 60)
        first_chunk = chunks[0]
        print(f"Chunk index: {first_chunk['chunk_index']}")
        print(f"Character count: {first_chunk['char_count']}")
        print(f"Document name: {first_chunk['document_name']}")
        print(f"\nText preview:")
        print(first_chunk['text'][:300] + "...\n")
        
        # Show last chunk details
        if len(chunks) > 1:
            print("-" * 60)
            print("LAST CHUNK DETAILS:")
            print("-" * 60)
            last_chunk = chunks[-1]
            print(f"Chunk index: {last_chunk['chunk_index']}")
            print(f"Character count: {last_chunk['char_count']}")
            print(f"\nText preview:")
            print(last_chunk['text'][:300] + "...\n")
        
        # Statistics
        print("=" * 60)
        print("STATISTICS")
        print("=" * 60)
        total_chars = sum(c['char_count'] for c in chunks)
        avg_chunk_size = total_chars / len(chunks)
        print(f"Total characters: {total_chars:,}")
        print(f"Average chunk size: {avg_chunk_size:.0f} characters")
        print(f"Smallest chunk: {min(c['char_count'] for c in chunks)} characters")
        print(f"Largest chunk: {max(c['char_count'] for c in chunks)} characters")
        
        print("\n✓ Document processor test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_document_processor()