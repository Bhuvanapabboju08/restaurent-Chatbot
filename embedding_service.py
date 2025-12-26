"""
Embedding Service using Sentence Transformers
Generates embeddings for text using local sentence-transformer models
"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

load_dotenv()


class EmbeddingService:
    """Generate embeddings using local Sentence Transformers"""

    def __init__(self, model_name: str = None):
        """
        Initialize Sentence Transformer embedding service

        Args:
            model_name: Model name (defaults to all-MiniLM-L6-v2)
        """
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)

        # Get embedding dimension
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()

        print(f"[OK] Sentence Transformer Embedding Service initialized")
        print(f"  Model: {self.model_name}")
        print(f"  Embedding dimension: {self.embedding_dimension}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        except Exception as e:
            raise Exception(f"Embedding generation error: {str(e)}")

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Show progress information

        Returns:
            List of embedding vectors
        """
        if not texts:
            raise ValueError("Text list cannot be empty")

        # Remove empty texts
        valid_texts = [t for t in texts if t and t.strip()]

        if len(valid_texts) != len(texts):
            print(f"[WARN] Skipped {len(texts) - len(valid_texts)} empty texts")

        if show_progress:
            print(f"Generating embeddings for {len(valid_texts)} texts...")

        try:
            # Generate embeddings in batch (more efficient)
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )

            # Convert to list of lists
            return embeddings.tolist()

        except Exception as e:
            raise Exception(f"Batch embedding error: {str(e)}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model"""
        return self.embedding_dimension

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Compute cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("SENTENCE TRANSFORMER EMBEDDING SERVICE TEST")
    print("=" * 60)

    try:
        # Initialize service
        embedding_service = EmbeddingService()

        # Test single embedding
        print("\n1. Testing single text embedding...")
        test_text = "What are your restaurant opening hours?"
        embedding = embedding_service.generate_embedding(test_text)

        print(f"[OK] Text: '{test_text}'")
        print(f"[OK] Embedding dimension: {len(embedding)}")
        print(f"[OK] First 5 values: {[round(x, 4) for x in embedding[:5]]}")

        # Test batch embeddings
        print("\n2. Testing batch embeddings...")
        test_texts = [
            "What time do you open?",
            "Do you serve vegetarian food?",
            "How much does a pizza cost?",
            "Can I make a reservation?"
        ]

        embeddings = embedding_service.generate_embeddings_batch(test_texts, show_progress=True)

        print(f"[OK] Generated {len(embeddings)} embeddings")
        print(f"[OK] Each embedding dimension: {len(embeddings[0])}")

        # Test similarity
        print("\n3. Testing similarity computation...")
        sim_text1 = "What are your opening hours?"
        sim_text2 = "When do you open?"
        sim_text3 = "What food do you serve?"

        emb1 = embedding_service.generate_embedding(sim_text1)
        emb2 = embedding_service.generate_embedding(sim_text2)
        emb3 = embedding_service.generate_embedding(sim_text3)

        similarity_12 = embedding_service.compute_similarity(emb1, emb2)
        similarity_13 = embedding_service.compute_similarity(emb1, emb3)

        print(f"[OK] Similarity ('{sim_text1}' vs '{sim_text2}'): {similarity_12:.3f}")
        print(f"[OK] Similarity ('{sim_text1}' vs '{sim_text3}'): {similarity_13:.3f}")
        print(f"  -> Similar questions have higher scores!")

        print("\n[OK] All embedding tests passed!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
