"""
Text chunking and embedding generation module.
"""

import requests
from llama_index.core.schema import TextNode

from app.settings import settings


def chunk_text_simple(text: str, max_bytes: int = 1024, overlap_bytes: int = 100) -> list[str]:
    """
    Byte-based chunking with overlap to handle Unicode properly.
    
    Conservative chunking to stay under token/byte limits:
    - 1024 bytes is a safe middle ground
    - Balances chunk size with processing speed
    
    Args:
        text: Text to chunk
        max_bytes: Maximum bytes per chunk (default 1024)
        overlap_bytes: Number of overlapping bytes between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    text_bytes = text.encode('utf-8')
    start = 0
    
    while start < len(text_bytes):
        # Take a chunk of bytes
        end = start + max_bytes
        chunk_bytes = text_bytes[start:end]
        
        # Decode, handling potential incomplete UTF-8 sequences at the end
        try:
            chunk = chunk_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # If we split in the middle of a multi-byte char, back up
            while end > start:
                end -= 1
                try:
                    chunk = text_bytes[start:end].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Shouldn't happen, but skip this chunk if we can't decode
                start = end + 1
                continue
        
        chunks.append(chunk)
        start = end - overlap_bytes
    
    return chunks


def get_embeddings_direct(texts: list[str]) -> list[list[float]]:
    """
    Call the embedding API directly to get embeddings.
    Sends one text at a time to avoid batch issues.
    
    Args:
        texts: List of text strings to embed
    
    Returns:
        List of embedding vectors
    """
    url = f"{settings.embedding_url}/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.embedding_key}",
        "Content-Type": "application/json"
    }
    
    embeddings = []
    for text in texts:
        payload = {
            "model": settings.embedding_model_id,
            "input": [text]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        embeddings.append(data["data"][0]["embedding"])
    
    return embeddings


def create_text_nodes_with_embeddings(
    content: str,
    metadata: dict,
    max_bytes: int = 1024,
    overlap_bytes: int = 100
) -> list[TextNode]:
    """
    Chunk text and create TextNodes with embeddings.
    
    Args:
        content: Text content to process
        metadata: Metadata to attach to each node
        max_bytes: Maximum bytes per chunk
        overlap_bytes: Number of overlapping bytes between chunks
    
    Returns:
        List of TextNode objects with embeddings
    """
    # Chunk the text
    chunks = chunk_text_simple(content, max_bytes=max_bytes, overlap_bytes=overlap_bytes)
    
    # Get embeddings
    embeddings = get_embeddings_direct(chunks)
    
    # Create nodes with embeddings and metadata
    nodes = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        node_metadata = {
            **metadata,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        
        node = TextNode(
            text=chunk,
            embedding=embedding,
            metadata=node_metadata
        )
        nodes.append(node)
    
    return nodes

