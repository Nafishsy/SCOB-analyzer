"""
PDF Processing Module for extracting text from legal documents
"""
import os
from typing import List, Dict
from pypdf import PdfReader
from pathlib import Path


class PDFProcessor:
    """Handles PDF text extraction and preprocessing"""

    def __init__(self, pdf_directory: str):
        self.pdf_directory = pdf_directory

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a single PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def process_all_pdfs(self) -> List[Dict[str, str]]:
        """
        Process all PDFs in the directory

        Returns:
            List of dictionaries containing document metadata and text
        """
        documents = []

        if not os.path.exists(self.pdf_directory):
            print(f"Directory not found: {self.pdf_directory}")
            return documents

        pdf_files = [f for f in os.listdir(self.pdf_directory)
                     if f.lower().endswith('.pdf')]

        print(f"Found {len(pdf_files)} PDF files")

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            print(f"Processing: {pdf_file}")

            text = self.extract_text_from_pdf(pdf_path)

            if text:
                documents.append({
                    'filename': pdf_file,
                    'filepath': pdf_path,
                    'text': text,
                    'source': 'SCOB 2015',
                    'year': '2015'
                })

        return documents

    def chunk_text(self, text: str, chunk_size: int = 1500,
                   overlap: int = 300, min_chunk_size: int = 200) -> List[str]:
        """
        Split text into overlapping chunks optimized for legal documents

        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Overlap between chunks in characters
            min_chunk_size: Minimum acceptable chunk size

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]

            # For legal documents, try to break at better boundaries
            if end < text_length:
                # Priority 1: Break at paragraph (double newline)
                paragraph_break = chunk.rfind('\n\n')

                # Priority 2: Break at numbered/lettered sections
                section_patterns = [
                    chunk.rfind('\n\n'),  # Paragraph
                    chunk.rfind('\n['),   # Numbered section like [23]
                    chunk.rfind('\n('),   # Subsection like (a)
                ]

                # Priority 3: Break at sentence boundary
                sentence_breaks = [
                    chunk.rfind('. '),
                    chunk.rfind('.\n'),
                ]

                # Find the best break point
                all_breaks = section_patterns + sentence_breaks
                valid_breaks = [b for b in all_breaks if b > chunk_size * 0.4]

                if valid_breaks:
                    break_point = max(valid_breaks)
                    # For paragraph breaks, include the newlines
                    if break_point == paragraph_break:
                        chunk = chunk[:break_point + 2]
                        end = start + break_point + 2
                    else:
                        chunk = chunk[:break_point + 1]
                        end = start + break_point + 1

            # Only add chunk if it meets minimum size
            chunk_text = chunk.strip()
            if len(chunk_text) >= min_chunk_size:
                chunks.append(chunk_text)

            start = end - overlap

            if start >= text_length:
                break

        return chunks
