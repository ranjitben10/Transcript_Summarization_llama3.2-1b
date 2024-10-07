import re

class RecursiveTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        # Try splitting by paragraphs (denoted by two or more newlines)
        chunks = self.split_by_delimiter(text, r'\n\n')
        if self.all_chunks_within_limit(chunks):
            return self.add_overlap(chunks)

        # If still too large, split by sentences (denoted by punctuation followed by space)
        chunks = self.split_by_delimiter(text, r'(?<=[.!?])\s+')
        if self.all_chunks_within_limit(chunks):
            return self.add_overlap(chunks)

        # If still too large, split by words (denoted by spaces)
        chunks = self.split_by_delimiter(text, ' ')
        return self.add_overlap(chunks)

    def split_by_delimiter(self, text, delimiter):
        """Split the text by a given delimiter."""
        return re.split(delimiter, text)

    def all_chunks_within_limit(self, chunks):
        """Check if all chunks are within the defined chunk size."""
        return all(len(chunk) <= self.chunk_size for chunk in chunks)

    def add_overlap(self, chunks):
        """Add overlap between chunks."""
        result = []
        current_chunk = ""

        for i, chunk in enumerate(chunks):
            if len(current_chunk) + len(chunk) <= self.chunk_size:
                current_chunk += chunk + " "
            else:
                # Add the current chunk to the result and include overlap
                result.append(current_chunk.strip())
                
                # Start a new chunk with the overlap from the previous chunk
                overlap = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap + chunk + " "
        
        # Add the last chunk
        if current_chunk:
            result.append(current_chunk.strip())
        
        return result

