"""
RAG Query Interface for Legal Document Search
"""
import sys
from pathlib import Path

# Add src and config directories to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from weaviate_manager import WeaviateManager
import rag_config as config


class RAGQuery:
    """RAG system for querying legal documents"""

    def __init__(self, chatbot_mode=False):
        self.weaviate_manager = WeaviateManager()
        self.chatbot_mode = chatbot_mode

        # Initialize OpenAI client for chatbot mode
        if self.chatbot_mode and config.OPENAI_API_KEY:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.openai_client = None

    def initialize(self):
        """Initialize connection to Weaviate"""
        if not self.weaviate_manager.connect():
            print("Failed to connect to Weaviate. Make sure it's running.")
            print("Run: docker-compose up -d (from SCOB_RAG directory)")
            return False
        return True

    def generate_answer(self, question: str, context_chunks: list) -> str:
        """
        Generate an answer using OpenAI with RAG context

        Args:
            question: User's question
            context_chunks: List of relevant document chunks

        Returns:
            Generated answer
        """
        # Combine context from top chunks
        context = "\n\n".join([chunk['text'] for chunk in context_chunks[:3]])

        # Create prompt
        system_prompt = """You are a legal expert assistant specializing in Bangladesh law.
Answer questions based ONLY on the provided legal document context.
If the context doesn't contain relevant information, say so clearly.
Cite specific sections, case names, or legal provisions when applicable."""

        user_prompt = f"""Context from legal documents:
{context}

Question: {question}

Please provide a clear, concise answer based on the context above."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {e}"

    def query(self, question: str, num_results: int = 5):
        """
        Query the RAG system

        Args:
            question: User's question
            num_results: Number of relevant chunks to retrieve
        """
        print("\n" + "=" * 60)
        print(f"Query: {question}")
        print("=" * 60)

        # Retrieve relevant documents
        results = self.weaviate_manager.search(question, limit=num_results)

        if not results:
            print("\nNo relevant documents found.")
            return

        # Chatbot mode - generate simple answer
        if self.chatbot_mode:
            print("\n📝 Answer:")
            print("-" * 60)
            answer = self.generate_answer(question, results)
            print(answer)
            print("-" * 60)

            print("\n📚 Sources:")
            for idx, result in enumerate(results[:3], 1):
                source_info = f"{idx}. {result['filename']}"
                if result.get('case_name'):
                    source_info += f" - {result['case_name']}"
                if result.get('citations'):
                    source_info += f" ({', '.join(result['citations'][:2])})"
                print(source_info)
            return

        # Standard mode - show detailed results
        print(f"\nFound {len(results)} relevant document chunks:\n")

        # Display results with metadata
        for idx, result in enumerate(results, 1):
            print(f"\n--- Result {idx} ---")
            print(f"Source: {result['filename']} (Chunk {result['chunk_index']})")
            print(f"Relevance Score: {1 - result['distance']:.4f}")

            # Display case metadata if available
            if result.get('case_name'):
                print(f"Case Name: {result['case_name']}")
            if result.get('case_number'):
                print(f"Case Number: {result['case_number']}")
            if result.get('court'):
                print(f"Court: {result['court']}")
            if result.get('judges') and len(result['judges']) > 0:
                print(f"Judges: {', '.join(result['judges'])}")
            if result.get('judgment_date'):
                print(f"Judgment Date: {result['judgment_date']}")
            if result.get('citations') and len(result['citations']) > 0:
                print(f"Citations: {', '.join(result['citations'])}")
            if result.get('subject_matter') and len(result['subject_matter']) > 0:
                print(f"Subject Matter: {', '.join(result['subject_matter'])}")

            print(f"\nText Preview:")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
            print("-" * 60)

        # Generate answer context
        print("\n" + "=" * 60)
        print("Context for Answer Generation:")
        print("=" * 60)
        context = "\n\n".join([r['text'] for r in results[:3]])
        print(context[:1000] + "..." if len(context) > 1000 else context)

    def interactive_mode(self):
        """Run interactive query mode"""
        print("\n" + "=" * 60)
        print("Legal Document RAG System - Interactive Mode")
        if self.chatbot_mode:
            print("Mode: Chatbot (AI-generated answers)")
        else:
            print("Mode: Search (Detailed document results)")
        print("=" * 60)
        print("Type 'exit' or 'quit' to stop")
        print("Type 'mode' to switch between chatbot/search mode\n")

        while True:
            try:
                question = input("\n🔍 Your question: ").strip()

                if question.lower() in ['exit', 'quit', 'q']:
                    print("Exiting...")
                    break

                if question.lower() == 'mode':
                    self.chatbot_mode = not self.chatbot_mode
                    mode_name = "Chatbot" if self.chatbot_mode else "Search"
                    print(f"Switched to {mode_name} mode")
                    continue

                if not question:
                    continue

                self.query(question)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break

    def close(self):
        """Close connections"""
        self.weaviate_manager.close()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Legal Document RAG Query System')
    parser.add_argument('query', nargs='*', help='Search query (leave empty for interactive mode)')
    parser.add_argument('--chat', '-c', action='store_true',
                       help='Chatbot mode: Get AI-generated answer with sources')
    parser.add_argument('--results', '-r', type=int, default=5,
                       help='Number of results to retrieve (default: 5)')

    args = parser.parse_args()

    # Initialize RAG with chatbot mode if requested
    rag = RAGQuery(chatbot_mode=args.chat)

    if not rag.initialize():
        return

    # Check if query provided as command line argument
    if args.query:
        question = " ".join(args.query)
        rag.query(question, num_results=args.results)
    else:
        # Interactive mode
        rag.interactive_mode()

    rag.close()


if __name__ == "__main__":
    main()
