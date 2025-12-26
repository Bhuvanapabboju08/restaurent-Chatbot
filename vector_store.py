"""
Vector Store Module
Simple in-memory vector store with pickle persistence (ChromaDB-free alternative)
"""

import os
import pickle
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """Manage vector storage and retrieval using in-memory storage with pickle persistence"""

    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize simple vector store

        Args:
            persist_directory: Path to persist data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR",
            "./data/chroma_db"
        )
        self.collection_name = collection_name or os.getenv(
            "COLLECTION_NAME",
            "restaurant_docs"
        )

        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)

        # Storage file path
        self.storage_file = os.path.join(
            self.persist_directory,
            f"{self.collection_name}.pkl"
        )

        # In-memory storage
        self.data = {
            "ids": [],
            "documents": [],
            "embeddings": [],
            "metadatas": []
        }

        # Load existing data if available
        self._load()

        print(f"[OK] Vector store initialized: {self.collection_name}")
        print(f"[OK] Storage location: {self.persist_directory}")
        print(f"[OK] Current document count: {self.count()}")

    def _load(self):
        """Load data from pickle file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'rb') as f:
                    self.data = pickle.load(f)
                print(f"[OK] Loaded {len(self.data['ids'])} chunks from storage")
            except Exception as e:
                print(f"[WARN] Could not load existing data: {e}")
                self.data = {
                    "ids": [],
                    "documents": [],
                    "embeddings": [],
                    "metadatas": []
                }

    def _save(self):
        """Save data to pickle file"""
        try:
            with open(self.storage_file, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            print(f"[WARN] Could not save data: {e}")

    def count(self) -> int:
        """Return number of chunks in store"""
        return len(self.data["ids"])

    def add_documents(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]],
        document_id: str
    ) -> int:
        """
        Add document chunks with embeddings to vector store

        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors
            document_id: Unique identifier for the document

        Returns:
            Number of chunks added
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique ID
            chunk_id = f"{document_id}_chunk_{idx}"

            # Prepare metadata
            metadata = {
                "document_id": document_id,
                "document_name": chunk.get("document_name", "unknown"),
                "document_hash": chunk.get("document_hash", ""),
                "chunk_index": chunk.get("chunk_index", idx),
                "total_chunks": chunk.get("total_chunks", len(chunks)),
                "char_count": chunk.get("char_count", len(chunk["text"]))
            }

            # Add to storage
            self.data["ids"].append(chunk_id)
            self.data["documents"].append(chunk["text"])
            self.data["embeddings"].append(embedding)
            self.data["metadatas"].append(metadata)

        # Persist to disk
        self._save()

        print(f"[OK] Added {len(chunks)} chunks to vector store")
        return len(chunks)

    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Dict = None
    ) -> Dict:
        """
        Query similar documents using embedding

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            Dictionary with results and metadata
        """
        if len(self.data["embeddings"]) == 0:
            return {"results": [], "count": 0}

        # Convert to numpy arrays
        query_vec = np.array(query_embedding).reshape(1, -1)
        embeddings_matrix = np.array(self.data["embeddings"])

        # Calculate cosine similarities
        similarities = cosine_similarity(query_vec, embeddings_matrix)[0]

        # Apply filters if provided
        valid_indices = list(range(len(similarities)))
        if filter_dict:
            valid_indices = [
                i for i in valid_indices
                if all(
                    self.data["metadatas"][i].get(k) == v
                    for k, v in filter_dict.items()
                )
            ]

        # Get top k indices
        if len(valid_indices) == 0:
            return {"results": [], "count": 0}

        valid_similarities = [(i, similarities[i]) for i in valid_indices]
        valid_similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [i for i, _ in valid_similarities[:top_k]]

        # Format results
        formatted_results = []
        for i in top_indices:
            result = {
                "id": self.data["ids"][i],
                "text": self.data["documents"][i],
                "metadata": self.data["metadatas"][i],
                "similarity": float(similarities[i])
            }
            formatted_results.append(result)

        return {
            "results": formatted_results,
            "count": len(formatted_results)
        }

    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks of a document

        Args:
            document_id: Document identifier

        Returns:
            Number of chunks deleted
        """
        # Find indices to delete
        indices_to_delete = [
            i for i, meta in enumerate(self.data["metadatas"])
            if meta.get("document_id") == document_id
        ]

        if not indices_to_delete:
            print(f"[WARN] No chunks found for document: {document_id}")
            return 0

        # Delete in reverse order to maintain indices
        for i in sorted(indices_to_delete, reverse=True):
            del self.data["ids"][i]
            del self.data["documents"][i]
            del self.data["embeddings"][i]
            del self.data["metadatas"][i]

        # Persist changes
        self._save()

        print(f"[OK] Deleted {len(indices_to_delete)} chunks for document: {document_id}")
        return len(indices_to_delete)

    def document_exists(self, document_hash: str) -> bool:
        """
        Check if document already exists in vector store

        Args:
            document_hash: MD5 hash of document

        Returns:
            True if document exists
        """
        for meta in self.data["metadatas"]:
            if meta.get("document_hash") == document_hash:
                return True
        return False

    def get_all_documents(self) -> List[Dict]:
        """
        Get list of all unique documents in store

        Returns:
            List of document information
        """
        documents = {}
        for metadata in self.data["metadatas"]:
            doc_id = metadata.get("document_id")
            if doc_id and doc_id not in documents:
                documents[doc_id] = {
                    "document_id": doc_id,
                    "document_name": metadata.get("document_name", "unknown"),
                    "document_hash": metadata.get("document_hash", ""),
                    "total_chunks": metadata.get("total_chunks", 0)
                }

        return list(documents.values())

    def get_stats(self) -> Dict:
        """
        Get vector store statistics

        Returns:
            Dictionary with statistics
        """
        total_chunks = self.count()
        documents = self.get_all_documents()

        return {
            "total_chunks": total_chunks,
            "total_documents": len(documents),
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }

    def reset_collection(self):
        """Reset/clear the entire collection (use with caution!)"""
        self.data = {
            "ids": [],
            "documents": [],
            "embeddings": [],
            "metadatas": []
        }
        self._save()
        print(f"[OK] Collection '{self.collection_name}' reset")


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("VECTOR STORE TEST")
    print("=" * 60)

    try:
        # Initialize vector store
        vector_store = VectorStore()

        # Show current stats
        stats = vector_store.get_stats()
        print(f"\nCurrent Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Total documents: {stats['total_documents']}")

        # Test adding sample data
        print("\n" + "=" * 60)
        print("Testing with sample data...")
        print("=" * 60)

        # Sample chunks
        sample_chunks = [
            {
                "text": "Our restaurant opens at 11 AM and closes at 11 PM daily.",
                "document_name": "restaurant_info.pdf",
                "document_hash": "test_hash_123",
                "chunk_index": 0,
                "total_chunks": 2,
                "char_count": 60
            },
            {
                "text": "We specialize in Italian cuisine with fresh ingredients.",
                "document_name": "restaurant_info.pdf",
                "document_hash": "test_hash_123",
                "chunk_index": 1,
                "total_chunks": 2,
                "char_count": 58
            }
        ]

        # Sample embeddings (random for testing - in real use, get from embedding service)
        import random
        sample_embeddings = [[random.random() for _ in range(384)] for _ in range(2)]

        # Add to vector store
        added = vector_store.add_documents(
            chunks=sample_chunks,
            embeddings=sample_embeddings,
            document_id="test_doc_001"
        )

        # Query test
        print("\n" + "=" * 60)
        print("Testing similarity search...")
        print("=" * 60)

        query_embedding = [random.random() for _ in range(384)]
        results = vector_store.query_similar(query_embedding, top_k=2)

        print(f"[OK] Found {results['count']} similar chunks")
        for idx, result in enumerate(results['results'], 1):
            print(f"\nResult {idx}:")
            print(f"  Text: {result['text'][:50]}...")
            print(f"  Similarity: {result['similarity']:.3f}")

        # List documents
        print("\n" + "=" * 60)
        print("All documents in store:")
        print("=" * 60)
        docs = vector_store.get_all_documents()
        for doc in docs:
            print(f"  - {doc['document_name']} (ID: {doc['document_id']}, Chunks: {doc['total_chunks']})")

        print("\n[OK] All vector store tests passed!")

        # Cleanup test data
        print("\nCleaning up test data...")
        vector_store.delete_document("test_doc_001")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
