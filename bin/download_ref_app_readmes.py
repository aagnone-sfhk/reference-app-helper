#!/usr/bin/env python3
"""
Download README files from all public repositories in the heroku-reference-apps GitHub organization
and generate embeddings using Heroku MIA and Cohere.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.embeddings import create_text_nodes_with_embeddings
from app.github import get_repositories, download_readme
from app.rag import create_vector_store


GITHUB_ORG = "heroku-reference-apps"
OUTPUT_DIR = "reference-app-readmes"


def generate_embeddings(content: str, repo_name: str, file_path: str, vector_store) -> bool:
    """
    Generate embeddings for the README content and store in vector database.
    
    Args:
        content: The README text content
        repo_name: Name of the repository
        file_path: Path to the README file
        vector_store: PGVectorStore instance
    
    Returns:
        True if embeddings were generated successfully
    """
    try:
        metadata = {
            "source": "heroku-reference-apps",
            "repo_name": repo_name,
            "file_path": file_path,
            "org": GITHUB_ORG,
        }
        
        # Create nodes with embeddings
        nodes = create_text_nodes_with_embeddings(
            content=content,
            metadata=metadata,
            max_bytes=1024,
            overlap_bytes=100
        )
        
        # Add nodes to vector store
        vector_store.add(nodes)
        
        print(f"  🔮 Generated embeddings for {repo_name} ({len(nodes)} chunks)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error generating embeddings for {repo_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to download all READMEs and generate embeddings."""
    print(f"🚀 Downloading READMEs from {GITHUB_ORG}")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}\n")
    
    # Initialize embedding infrastructure
    print("🔧 Initializing vector store...")
    try:
        vector_store = create_vector_store()
        print("✅ Vector store ready\n")
    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")
        print("⚠️  Will download files but skip embedding generation\n")
        vector_store = None
    
    # Get all repositories
    print(f"📚 Fetching repositories from {GITHUB_ORG}...")
    repos = get_repositories(GITHUB_ORG)
    
    if not repos:
        print("❌ No repositories found or error fetching repositories")
        sys.exit(1)
    
    print(f"Found {len(repos)} repositories\n")
    
    # Download README for each repository and generate embeddings
    download_count = 0
    embedding_count = 0
    
    for repo in repos:
        repo_name = repo["name"]
        print(f"📄 {repo_name}")
        
        success, content, file_path = download_readme(GITHUB_ORG, repo_name, output_dir)
        
        if success:
            if file_path and Path(file_path).exists():
                # Check if this was an existing file
                print(f"  ✅ README available ({len(content)} bytes)")
            download_count += 1
            
            # Generate embeddings if infrastructure is available and content exists
            if vector_store is not None and content:
                if generate_embeddings(content, repo_name, file_path, vector_store):
                    embedding_count += 1
        else:
            print(f"  ⚠️  No README found for {repo_name}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Downloaded {download_count}/{len(repos)} READMEs")
    print(f"🔮 Generated embeddings for {embedding_count}/{download_count} READMEs")
    print(f"📂 Files saved to: {output_dir.absolute()}")
    print(f"💾 Embeddings stored in PostgreSQL vector database")


if __name__ == "__main__":
    main()

