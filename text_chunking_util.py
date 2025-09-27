from abc import ABC, abstractmethod
from typing import List


class TextChunkCreator(ABC):
    """Abstract base class for text chunking providers"""

    @abstractmethod
    def convertTextToChunks(self, text: str, separator: str) -> List[str]:
        """
        Convert large text into chunks based on separator

        Args:
            text: Large text to be chunked
            separator: String to use for separating text

        Returns:
            List[str]: Array of text chunks
        """
        pass


class SimpleTextChunkCreator(TextChunkCreator):
    """Simple text chunker that splits text based on separator"""

    def convertTextToChunks(self, text: str, separator: str) -> List[str]:
        """
        Split text into chunks using the provided separator

        Args:
            text: Large text to be chunked
            separator: String to use for separating text

        Returns:
            List[str]: Array of text chunks with separator removed
        """
        if not text:
            return []

        if not separator:
            return [text]

        # Split by separator and filter out empty strings
        chunks = [chunk.strip() for chunk in text.split(separator) if chunk.strip()]
        chunks = [chunk for chunk in chunks if chunk]  # filter out empty strings

        return chunks