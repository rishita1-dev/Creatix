import os
import time

import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv


load_dotenv()


class GeminiEmbeddings:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file."
            )

        genai.configure(api_key=api_key)

        self.model_name = "models/gemini-embedding-001"

    def embed_document(self, text):
        """
        Create an embedding for repository code/text.
        """

        response = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document",
        )

        return np.array(
            response["embedding"],
            dtype=np.float32,
        )

    def embed_query(self, query):
        """
        Create an embedding for a user's question.
        """

        response = genai.embed_content(
            model=self.model_name,
            content=query,
            task_type="retrieval_query",
        )

        return np.array(
            response["embedding"],
            dtype=np.float32,
        )

    def embed_documents(self, texts):
        """
        Create embeddings for multiple text chunks.
        """

        embeddings = []

        for index, text in enumerate(texts):

            try:
                embedding = self.embed_document(text)

                embeddings.append(embedding)

            except Exception as e:

                raise RuntimeError(
                    f"Failed to embed chunk {index}: {e}"
                )

            # Small delay to reduce API rate-limit problems
            time.sleep(0.1)

        return np.array(
            embeddings,
            dtype=np.float32,
        )