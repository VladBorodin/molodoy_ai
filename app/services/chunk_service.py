import re


class ChunkService:
	def split_text(self, text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
		normalized_text = self._normalize_text(text)

		if not normalized_text:
			return []

		chunks = []
		start_position = 0

		while start_position < len(normalized_text):
			end_position = start_position + chunk_size
			chunk = normalized_text[start_position:end_position].strip()

			if chunk:
				chunks.append(chunk)

			if end_position >= len(normalized_text):
				break

			start_position = end_position - overlap

		return chunks

	def _normalize_text(self, text: str) -> str:
		return re.sub(r"\s+", " ", text).strip()