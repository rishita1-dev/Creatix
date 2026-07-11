import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class CodeVectorStore:
    """
    Stores repository code chunks as vector embeddings
    and retrieves the most relevant chunks for a question.
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")

        self.model = SentenceTransformer(model_name)

        self.index = None
        self.chunks = []


    def build_index(self, chunks):
        """
        Convert all code chunks into embeddings
        and store them in a FAISS index.
        """

        if not chunks:
            raise ValueError("No chunks provided to build the index.")

        self.chunks = chunks

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        print(f"Creating embeddings for {len(texts)} chunks...")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        embeddings = embeddings.astype("float32")

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(
            f"Vector index created successfully "
            f"with {self.index.ntotal} vectors."
        )


    def search(self, query, top_k=5):
        """
        Find the code chunks most relevant to the user's question.
        """

        if self.index is None:
            raise ValueError(
                "Vector index has not been built yet."
            )

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            chunk = self.chunks[index]

            results.append({
                "file_path": chunk["file_path"],
                "chunk_number": chunk["chunk_number"],
                "content": chunk["content"],
                "score": float(score)
            })

        return results