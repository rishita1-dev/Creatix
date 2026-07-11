def chunk_documents(documents, chunk_size=1500, overlap=200):
    """
    Split repository files into smaller overlapping chunks.

    Args:
        documents: List of dictionaries containing
                   'file_path' and 'content'.
        chunk_size: Maximum number of characters in each chunk.
        overlap: Number of characters shared between consecutive chunks.

    Returns:
        List of chunk dictionaries.
    """

    chunks = []

    for document in documents:
        file_path = document["file_path"]
        content = document["content"]

        # Skip empty files
        if not content.strip():
            continue

        start = 0
        chunk_number = 0

        while start < len(content):
            end = start + chunk_size
            chunk_content = content[start:end]

            chunks.append({
                "file_path": file_path,
                "chunk_number": chunk_number,
                "content": chunk_content
            })

            chunk_number += 1

            # Move forward while keeping some overlap
            start += chunk_size - overlap

    return chunks