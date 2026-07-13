class CodeChunker:

    def __init__(
        self,
        chunk_size=1500,
        chunk_overlap=200,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents):
        """
        Split repository files into smaller overlapping chunks.
        """

        chunks = []

        for document in documents:

            path = document["path"]
            content = document["content"]

            start = 0

            while start < len(content):

                end = start + self.chunk_size

                chunk_text = content[start:end]

                if chunk_text.strip():
                    chunks.append(
                        {
                            "path": path,
                            "content": chunk_text,
                            "start": start,
                            "end": min(
                                end,
                                len(content)
                            ),
                        }
                    )

                if end >= len(content):
                    break

                start = end - self.chunk_overlap

        return chunks