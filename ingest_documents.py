"""
Ingestion Script to load PDFs into Weaviate
Run this script to process PDFs and populate the vector database
"""
import sys
from pathlib import Path

# Add src and config directories to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from pdf_processor import PDFProcessor
from weaviate_manager import WeaviateManager
import rag_config as config


def main():
    """Main ingestion pipeline"""
    print("=" * 60)
    print("Legal Document RAG System - Data Ingestion")
    print("=" * 60)

    # Step 1: Extract text from PDFs
    print("\n[Step 1] Extracting text from PDFs...")
    print(f"PDF Directory: {config.PDF_BASE_DIR}")
    pdf_processor = PDFProcessor(config.PDF_BASE_DIR)
    documents = pdf_processor.process_all_pdfs()

    if not documents:
        print("No documents found to process. Exiting.")
        return

    print(f"Successfully extracted text from {len(documents)} documents")

    # Step 2: Connect to Weaviate
    print("\n[Step 2] Connecting to Weaviate...")
    weaviate_manager = WeaviateManager()

    if not weaviate_manager.connect():
        print("\nFailed to connect to Weaviate.")
        print("Please ensure Weaviate is running:")
        print("\nTo start Weaviate with Docker Compose:")
        print("  cd SCOB_RAG")
        print("  docker-compose up -d")
        return

    # Step 3: Create schema
    print("\n[Step 3] Creating Weaviate schema...")
    if not weaviate_manager.create_schema():
        print("Failed to create schema. Exiting.")
        weaviate_manager.close()
        return

    # Step 4: Add documents to Weaviate
    print("\n[Step 4] Adding documents to Weaviate...")
    print(f"Using chunk size: {config.CHUNK_SIZE}")
    print(f"Using chunk overlap: {config.CHUNK_OVERLAP}")

    weaviate_manager.add_documents(
        documents,
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )

    # Step 5: Cleanup
    print("\n[Step 5] Cleaning up...")
    weaviate_manager.close()

    print("\n" + "=" * 60)
    print("Ingestion completed successfully!")
    print("=" * 60)
    print("\nYou can now run 'python rag_query.py' to query the system")


if __name__ == "__main__":
    main()
