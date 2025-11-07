#!/usr/bin/env python3
"""
Reset Weaviate database - clears all data and recreates the schema from scratch
Also optionally clears uploaded PDF files and session data
"""

import sys
from pathlib import Path
import shutil

# Add src and config directories to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from weaviate_manager import WeaviateManager
import rag_config as config

def reset_weaviate(clear_files=True, clear_sessions=True):
    """
    Reset Weaviate database

    Args:
        clear_files: If True, also delete all uploaded PDF files
        clear_sessions: If True, also delete all chat session data
    """
    print("=" * 70)
    print("WEAVIATE DATABASE RESET - START FROM SCRATCH")
    print("=" * 70)

    # Initialize manager
    manager = WeaviateManager()

    # Connect to Weaviate
    print("\n1. Connecting to Weaviate...")
    if not manager.connect():
        print("ERROR: Could not connect to Weaviate!")
        print("Make sure Weaviate is running:")
        print("  docker-compose up -d")
        return False
    print("   ✓ Connected successfully")

    # Delete existing collection
    print("\n2. Clearing Weaviate collection...")
    try:
        if manager.client.collections.exists(config.COLLECTION_NAME):
            manager.client.collections.delete(config.COLLECTION_NAME)
            print(f"   ✓ Deleted collection: {config.COLLECTION_NAME}")
        else:
            print(f"   ✓ Collection '{config.COLLECTION_NAME}' was already empty")
    except Exception as e:
        print(f"   ERROR: Failed to delete collection: {e}")
        return False

    # Create fresh schema
    print("\n3. Creating fresh schema...")
    try:
        manager.create_schema()
        print("   ✓ Schema created successfully")
    except Exception as e:
        print(f"   ERROR: Failed to create schema: {e}")
        return False

    # Close connection
    print("\n4. Closing Weaviate connection...")
    manager.close()
    print("   ✓ Connection closed")

    # Clear uploaded PDFs
    if clear_files:
        print("\n5. Clearing uploaded PDF files...")
        uploads_dir = Path(config.PDF_BASE_DIR).parent.parent / "uploads"
        if uploads_dir.exists():
            pdf_count = len(list(uploads_dir.glob("*.pdf")))
            if pdf_count > 0:
                for pdf_file in uploads_dir.glob("*.pdf"):
                    pdf_file.unlink()
                print(f"   ✓ Deleted {pdf_count} PDF file(s)")
            else:
                print("   ✓ No PDF files to delete")
        else:
            print(f"   ✓ Uploads directory doesn't exist: {uploads_dir}")
    else:
        print("\n5. Skipping PDF file deletion (--keep-files flag used)")

    # Clear session data
    if clear_sessions:
        print("\n6. Clearing chat sessions...")
        sessions_dir = Path(__file__).parent / "sessions"
        if sessions_dir.exists():
            session_count = len(list(sessions_dir.glob("*.json")))
            if session_count > 0:
                shutil.rmtree(sessions_dir)
                print(f"   ✓ Deleted {session_count} session file(s)")
            else:
                print("   ✓ No session files to delete")
        else:
            print("   ✓ Sessions directory doesn't exist")
    else:
        print("\n6. Skipping session data deletion (--keep-sessions flag used)")

    print("\n" + "=" * 70)
    print("✓ RESET COMPLETE - System is now clean and ready for fresh data!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Start the backend:  python backend_api.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Upload your PDF files via the web interface at http://localhost:3000")
    print("\nOr use the CLI for batch ingestion:")
    print("  python ingest_documents.py <path_to_pdf_directory>")

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reset Weaviate database and optionally clear uploaded files")
    parser.add_argument("--keep-files", action="store_true", help="Keep uploaded PDF files (only reset Weaviate)")
    parser.add_argument("--keep-sessions", action="store_true", help="Keep chat session data")

    args = parser.parse_args()

    success = reset_weaviate(
        clear_files=not args.keep_files,
        clear_sessions=not args.keep_sessions
    )
    sys.exit(0 if success else 1)
