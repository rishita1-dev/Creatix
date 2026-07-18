import faiss
import numpy as np


class FAISSVectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []
        self.metadata = []

    def build_index(
        self,
        embeddings,
        chunks,
        metadata=None,
    ):
        """
        Build a FAISS index from repository embeddings.
        """

        if len(embeddings) == 0:
            raise ValueError(
                "Cannot build index with zero embeddings."
            )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        dimension = embeddings.shape[1]

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.chunks = chunks

        if metadata is None:
            self.metadata = [{} for _ in chunks]
        else:
            self.metadata = metadata

    def search(
        self,
        query_embedding,
        top_k=5,
    ):
        """
        Find the most relevant repository chunks.
        """

        if self.index is None:
            raise ValueError(
                "FAISS index has not been built."
            )

        query_embedding = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        faiss.normalize_L2(query_embedding)

        actual_k = min(
            top_k,
            len(self.chunks),
        )

        scores, indices = self.index.search(
            query_embedding,
            actual_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index == -1:
                continue

            chunk = self.chunks[index].copy()

            chunk["score"] = float(score)

            if index < len(self.metadata):
                chunk["metadata"] = self.metadata[index]

            results.append(chunk)

        return results

    def clear(self):
        """
        Clears the FAISS index.
        """

        self.index = None
        self.chunks = []
        self.metadata = []