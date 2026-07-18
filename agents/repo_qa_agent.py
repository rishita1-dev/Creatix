import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

from rag.repo_loader import RepoLoader
from rag.code_chunker import CodeChunker
from rag.vector_store import FAISSVectorStore
from llm.embeddings import GeminiEmbeddings

load_dotenv()


class RepoQAAgent:
    """
    Repository Question Answering Agent using
    AST + RAG.
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

        self.ast_index = None
        self.current_repo = None

    def load_repository(self, repo_url):

        print("=" * 60)
        print("Loading Repository...")
        print("=" * 60)

        repo_data = self.repo_loader.load_repository(repo_url)

        documents = repo_data["documents"]
        self.ast_index = repo_data["ast_index"]

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

        print("\n========== AST DEBUG ==========")

        print("Function names in AST:")
        print(list(self.ast_index.function_index.keys()))

        print("\nClass names in AST:")
        print(list(self.ast_index.class_index.keys()))

        print("===============================\n")

        return {
            "files_loaded": len(documents),
            "chunks_created": len(chunks),
            "functions": len(self.ast_index.function_index),
            "classes": len(self.ast_index.class_index),
        }

    # ----------------------------------------------------
    # AST LOOKUP
    # ----------------------------------------------------

    def ast_lookup(self, question):

        if self.ast_index is None:
            return None

        question_lower = question.lower()

        match = re.search(
            r"(function|method)\s+([A-Za-z_][A-Za-z0-9_]*)",
            question_lower,
        )

        if match:

            function_name = match.group(2)

            result = self.ast_index.get_function(
                function_name
            )

            if result:

                return (
                    f"Function '{function_name}' "
                    f"is defined in\n\n"
                    f"{result['file']}\n\n"
                    f"Line {result['data']['line']}"
                )

        match = re.search(
            r"class\s+([A-Za-z_][A-Za-z0-9_]*)",
            question_lower,
        )

        if match:

            class_name = match.group(1)

            result = self.ast_index.get_class(
                class_name
            )

            if result:

                return (
                    f"Class '{class_name}' "
                    f"is defined in\n\n"
                    f"{result['file']}\n\n"
                    f"Line {result['data']['line']}"
                )

        return None

    # ----------------------------------------------------
    # ASK
    # ----------------------------------------------------

    def ask(self, question, top_k=5):

        if self.vector_store.index is None:
            raise ValueError(
                "Repository has not been loaded yet."
            )

        # FIRST TRY AST
        ast_answer = self.ast_lookup(question)
        

        if ast_answer:
            return ast_answer

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

Answer clearly.
Mention filenames.
Do not hallucinate.
"""

        response = self.model.generate_content(prompt)

        return response.text