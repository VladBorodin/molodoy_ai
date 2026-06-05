import re


class SearchService:
	def find_relevant_chunks(
		self,
		question: str,
		chunk_contents: list[str],
		limit: int = 3
	) -> list[str]:
		question_words = self._extract_words(question)

		if not question_words:
			return []

		scored_chunks = []

		for chunk_content in chunk_contents:
			score = self._calculate_score(question_words, chunk_content)

			if score > 0:
				scored_chunks.append((score, chunk_content))

		scored_chunks.sort(key=lambda item: item[0], reverse=True)

		return [
			chunk_content
			for score, chunk_content in scored_chunks[:limit]
		]

	def _calculate_score(self, question_words: set[str], chunk_content: str) -> int:
		chunk_words = self._extract_words(chunk_content)
		matched_words = question_words.intersection(chunk_words)

		return len(matched_words)

	def _extract_words(self, text: str) -> set[str]:
		words = re.findall(r"[а-яА-ЯёЁa-zA-Z0-9]+", text.lower())

		return {
			word
			for word in words
			if len(word) > 2
		}