"""Base classes and implementations for chat agents with conversation memory."""

from typing import List, Optional, Tuple
from langroid.mytypes import Document
from abc import ABC, abstractmethod
from langroid.vector_store.base import VectorStore


class BaseMemoryChatAgent(ABC):
    """Base class with shared memory functionality."""

    vecdb: Optional[VectorStore] = None

    def __init__(self, username: Optional[str] = None) -> None:
        """Initialize BaseMemoryChatAgent."""
        self.username = username

    @abstractmethod
    def _store_document(self, document: Document) -> None:
        """Store document in vector database."""

    @abstractmethod
    def _create_conversation_document(self, message: str, response: str) -> Document:
        """Create conversation document from message and response."""

    def store_conversation(self, message: str | None, response: str) -> None:
        """Store conversation turn in vector database."""
        if self.vecdb is None or not message:
            return

        # Check if similar content already exists
        similar = self.vecdb.similar_texts_with_scores(
            text=message,
            k=1,
        )
        if similar and similar[0][1] > 0.95:
            return

        # Create conversation document (implementation specific to child classes)
        conversation = self._create_conversation_document(message, response)
        self._store_document(conversation)

    def get_relevant_context(self, query: Optional[str], k: int = 3) -> str:
        """Context retrieval with filtering and timestamp sorting."""
        if self.vecdb is None:
            return ""

        # If query is empty or None, get most recent messages
        if not query or query.strip() == "":
            return self._get_recent_context(k)

        # Get more results initially
        results = self.vecdb.similar_texts_with_scores(
            text=query,
            k=k * 2,
        )
        if not results:
            return self.get_relevant_context(None, k)

        # Filter and sort results
        filtered_results = self._filter_and_sort_results(results, k)

        if filtered_results:
            context = "\n---\n".join([doc.content for doc in filtered_results])
            return f"\nRelevant conversation history:\n{context.strip()}"

        return self.get_relevant_context(None, k)

    def _get_recent_context(self, k: int) -> str:
        """Get recent conversation context."""
        all_docs = self.vecdb.get_all_documents()
        sorted_docs = sorted(
            all_docs,
            key=lambda x: x.metadata.timestamp if hasattr(x.metadata, "timestamp") else "",
            reverse=True,
        )
        recent_docs = sorted_docs[:k]
        if recent_docs:
            context = "\n---\n".join([doc.content for doc in recent_docs])
            return f"\nRecent conversation history:\n{context.strip()}"
        return ""

    def _filter_and_sort_results(self, results: List[Tuple[Document, float]], k: int) -> List[Document]:
        """Filter and sort search results."""
        filtered_results = []
        seen_content = set()

        for doc, score in results:
            content = doc.content.strip()
            if content not in seen_content and score > 0.7:
                filtered_results.append(doc)
                seen_content.add(content)

        filtered_results.sort(
            key=lambda x: x.metadata.timestamp if hasattr(x.metadata, "timestamp") else "", reverse=True
        )

        return filtered_results[:k]

    def generate_system_prompt(self) -> str:
        """Generate system prompt with relevant context."""
        prompt = f"""You are a helpful assistant with conversation memory.
        You are talking to {self.username}."""

        history = self.get_relevant_context("")
        if history:
            prompt += f"\n\nhere some of the past messages:\n{history}"

        return prompt + "\n\nPlease start the conversation."

    def _get_enriched_message(self, message_str: str) -> str:
        """Add history context to user message."""
        context = self.get_relevant_context(message_str) if message_str else None

        if context:
            enhanced_prompt = (
                f"HISTORY:\n{context}\n\n"
                f"Current message: {message_str}\n\n"
                "Respond to the current message, using the previous conversations "
                "to personalize your response when relevant."
            )
        else:
            enhanced_prompt = message_str

        return enhanced_prompt
