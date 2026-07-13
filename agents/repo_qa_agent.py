import os
from dotenv import load_dotenv
import google.generativeai as genai

from rag.repo_loader import RepoLoader
from rag.code_chunker import CodeChunker
from rag.vector_store import FAISSVectorStore
from llm.embeddings import GeminiEmbeddings

load_dotenv()


class RepoQAAgent:
    """
    Repository Question Answering Agent using RAG.
    """

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-3.5-flash")

        self.repo_loader = RepoLoader()
        self.chunker = CodeChunker()
        self.embeddings = GeminiEmbeddings()
        self.vector_store = FAISSVectorStore()

        self.current_repo = None

    def load_repository(self, repo_url):

        print("=" * 60)
        print("Loading Repository...")
        print("=" * 60)

        documents = self.repo_loader.load_repository(repo_url)

        print(f"Loaded {len(documents)} files")

        chunks = self.chunker.chunk_documents(documents)

        print(f"Created {len(chunks)} chunks")

        texts = []

        for chunk in chunks:

            texts.append(
                f"File: {chunk['path']}\n\n{chunk['content']}"
            )

        print("Generating embeddings...")

        embeddings = self.embeddings.embed_documents(texts)

        print("Building FAISS Index...")

        self.vector_store.build_index(
            embeddings,
            chunks
        )

        self.current_repo = repo_url

        self.repo_loader.cleanup()

        print("Repository Ready!")

        return {
            "files_loaded": len(documents),
            "chunks_created": len(chunks)
        }

    def ask(self, question, top_k=5):

        if self.vector_store.index is None:
            raise ValueError(
                "Repository has not been loaded yet."
            )

        print("Searching repository...")

        query_embedding = self.embeddings.embed_query(
            question
        )

        relevant_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        if not relevant_chunks:
            return "No relevant repository context found."

        context = ""

        for chunk in relevant_chunks:

            context += f"""
FILE:
{chunk['path']}

CODE:
{chunk['content']}

----------------------------------
"""

        prompt = f"""
You are an expert software engineer.

Use ONLY the repository context below.

Repository Context:

{context}

Question:

{question}

Answer the question clearly.
Mention file names whenever appropriate.
Do not hallucinate.
"""

        response = self.model.generate_content(prompt)

        return response.text