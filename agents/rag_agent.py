import os

import google.generativeai as genai
from dotenv import load_dotenv

from rag.repo_loader import RepoLoader
from rag.code_chunker import CodeChunker
from rag.vector_store import FAISSVectorStore
from llm.embeddings import GeminiEmbeddings


load_dotenv()


class RAGAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file."
            )

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        self.repo_loader = RepoLoader()

        self.chunker = CodeChunker(
            chunk_size=1500,
            chunk_overlap=200
        )

        self.embeddings = GeminiEmbeddings()

        self.vector_store = FAISSVectorStore()

        self.current_repo_url = None


    def prepare_repository(self, repo_url):
        """
        Load repository, split files into chunks,
        create embeddings, and build the FAISS index.
        """

        # Don't rebuild if the same repository is already loaded
        if (
            self.current_repo_url == repo_url
            and self.vector_store.index is not None
        ):
            return

        documents = self.repo_loader.load_repository(
            repo_url
        )

        chunks = self.chunker.chunk_documents(
            documents
        )

        if not chunks:
            raise ValueError(
                "No code chunks could be generated."
            )

        texts_for_embedding = []

        for chunk in chunks:
            text = (
                f"File: {chunk['path']}\n\n"
                f"{chunk['content']}"
            )

            texts_for_embedding.append(text)

        embeddings = self.embeddings.embed_documents(
            texts_for_embedding
        )

        self.vector_store.build_index(
            embeddings=embeddings,
            chunks=chunks
        )

        self.current_repo_url = repo_url


    def answer_question(
        self,
        repo_url,
        question,
        top_k=5
    ):
        """
        Answer a question using relevant repository context.
        """

        if not repo_url or not repo_url.strip():
            return "Repository URL is required."

        if not question or not question.strip():
            return "Please enter a repository question."

        try:
            # Prepare the repository for RAG
            self.prepare_repository(repo_url)

            # Convert user question into an embedding
            query_embedding = self.embeddings.embed_query(
                question
            )

            # Search FAISS for relevant code chunks
            relevant_chunks = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )

            context_parts = []

            for chunk in relevant_chunks:
                context_parts.append(
                    f"""
FILE: {chunk['path']}

CODE:
{chunk['content']}
"""
                )

            context = "\n\n".join(context_parts)

            prompt = f"""
You are Creatix, an intelligent AI coding assistant.

Answer the user's question using only the repository context
provided below.

If the answer cannot be determined from the available repository
context, clearly say that there is not enough information.

Do not invent files, functions, classes, or implementation details.

REPOSITORY CONTEXT:

{context}

USER QUESTION:

{question}

Provide:
1. A direct answer.
2. Relevant file names.
3. Important functions or classes involved.
4. A clear technical explanation.
"""

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            return (
                "Repository Q&A Error: "
                f"{str(e)}"
            )

        finally:
            self.repo_loader.cleanup()