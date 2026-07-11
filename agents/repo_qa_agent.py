import os
from dotenv import load_dotenv
import google.generativeai as genai

from rag.repo_loader import load_github_repository
from rag.code_chunker import chunk_documents
from rag.vector_store import CodeVectorStore


load_dotenv()


class RepoQAAgent:
    """
    Repository Q&A Agent.

    It:
    1. Loads a GitHub repository.
    2. Splits repository files into chunks.
    3. Creates a vector index.
    4. Retrieves relevant chunks for a question.
    5. Sends only relevant context to Gemini.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file."
            )

        genai.configure(api_key=api_key)
        self.vector_store = None
        self.repo_url = None


    def load_repository(self, repo_url):
        """
        Load and index a GitHub repository.
        """

        print("Loading GitHub repository...")

        documents = load_github_repository(repo_url)

        if not documents:
            raise ValueError(
                "No supported files were found in the repository."
            )

        print(f"Loaded {len(documents)} files.")

        print("Creating code chunks...")

        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError(
                "No code chunks could be created."
            )

        print(f"Created {len(chunks)} chunks.")

        print("Building vector index...")

        self.vector_store = CodeVectorStore()
        self.vector_store.build_index(chunks)

        self.repo_url = repo_url

        return {
            "files_loaded": len(documents),
            "chunks_created": len(chunks)
        }
    
    def load_repository(self, repo_url):

        print("========== LOADING REPOSITORY ==========")
        print("Repo URL:", repo_url)

        documents = load_github_repository(repo_url)

        print("Documents loaded:", len(documents))

        chunks = chunk_documents(documents)

        print("Chunks created:", len(chunks))

        self.vector_store = CodeVectorStore()

        print("Building vector index...")

        self.vector_store.build_index(chunks)

        print("Vector index built successfully!")

        self.repo_url = repo_url

        return {
            "files_loaded": len(documents),
            "chunks_created": len(chunks)
        }


    def ask(self, question, top_k=5):
        """
        Answer a question using relevant repository context.
        """

        if self.vector_store is None:
            raise ValueError(
                "Repository has not been loaded yet."
            )

        relevant_chunks = self.vector_store.search(
            query=question,
            top_k=top_k
        )

        if not relevant_chunks:
            return "No relevant repository context was found."

        context_parts = []

        for chunk in relevant_chunks:
            context_parts.append(
                f"""
FILE: {chunk['file_path']}
CHUNK: {chunk['chunk_number']}

{chunk['content']}
"""
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""
You are an AI coding assistant analyzing a GitHub repository.

Answer the user's question using the repository context provided below.

Rules:
- Base your answer primarily on the provided repository code.
- Mention relevant file names when useful.
- Do not invent functions, classes, APIs, or files that are not present in the context.
- If the context is insufficient, clearly say so.
- Explain the answer clearly and technically.

REPOSITORY CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(prompt)

        return response.text