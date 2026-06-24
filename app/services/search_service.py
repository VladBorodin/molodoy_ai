import re
from dataclasses import dataclass

from app.models import KnowledgeChunk
from app.settings import settings


@dataclass(frozen=True)
class SearchResult:
	chunk_id: int
	entry_id: int
	entry_title: str
	position: int
	content: str
	score: int


class SearchService:
	def find_relevant_chunks(
		self,
		question: str,
		chunks: list[KnowledgeChunk],
		limit: int | None = None
	) -> list[SearchResult]:
		limit = limit or settings.rag_max_context_chunks

		question_words = self._extract_words(question)

		if not question_words:
			return []

		results = []

		for chunk in chunks:
			entry_title = chunk.entry.title if chunk.entry else ""

			score = self._calculate_score(
				question_words=question_words,
				chunk_content=chunk.content,
				entry_title=entry_title
			)

			if score <= 0:
				continue

			results.append(
				self._build_search_result(
					chunk=chunk,
					score=score
				)
			)

		results.sort(key=lambda item: item.score, reverse=True)

		return results[:limit]

	def get_general_context_chunks(
		self,
		chunks: list[KnowledgeChunk],
		limit: int | None = None
	) -> list[SearchResult]:
		limit = limit or settings.rag_max_context_chunks

		if not chunks:
			return []

		selected_results = []
		selected_chunk_ids = set()
		used_entry_ids = set()

		# Сначала берём первые чанки разных записей, чтобы дать ИИ обзор базы знаний.
		for chunk in chunks:
			if chunk.entry_id in used_entry_ids:
				continue

			selected_results.append(
				self._build_search_result(
					chunk=chunk,
					score=0
				)
			)

			selected_chunk_ids.add(chunk.id)
			used_entry_ids.add(chunk.entry_id)

			if len(selected_results) >= limit:
				return selected_results

		# Если записей мало, добираем оставшиеся чанки по порядку.
		for chunk in chunks:
			if chunk.id in selected_chunk_ids:
				continue

			selected_results.append(
				self._build_search_result(
					chunk=chunk,
					score=0
				)
			)

			if len(selected_results) >= limit:
				break

		return selected_results

	def _build_search_result(
		self,
		chunk: KnowledgeChunk,
		score: int
	) -> SearchResult:
		entry_title = chunk.entry.title if chunk.entry else ""

		return SearchResult(
			chunk_id=chunk.id,
			entry_id=chunk.entry_id,
			entry_title=entry_title,
			position=chunk.position,
			content=chunk.content,
			score=score
		)

	def _calculate_score(
		self,
		question_words: set[str],
		chunk_content: str,
		entry_title: str
	) -> int:
		chunk_words = self._extract_words(chunk_content)
		title_words = self._extract_words(entry_title)

		question_stems = self._build_stems(question_words)
		chunk_stems = self._build_stems(chunk_words)
		title_stems = self._build_stems(title_words)

		exact_chunk_matches = question_words.intersection(chunk_words)
		exact_title_matches = question_words.intersection(title_words)

		stem_chunk_matches = question_stems.intersection(chunk_stems)
		stem_title_matches = question_stems.intersection(title_stems)

		score = 0

		score += len(exact_chunk_matches) * 10
		score += len(exact_title_matches) * 15

		score += len(stem_chunk_matches) * 5
		score += len(stem_title_matches) * 8

		normalized_chunk = self._normalize_text(chunk_content)
		normalized_title = self._normalize_text(entry_title)

		for word in question_words:
			if len(word) < 4:
				continue

			if word in normalized_chunk:
				score += 2

			if word in normalized_title:
				score += 4

		return score

	def _extract_words(self, text: str) -> set[str]:
		normalized_text = self._normalize_text(text)
		words = re.findall(r"[а-яa-z0-9]+", normalized_text)

		return {
			word
			for word in words
			if len(word) > 2
		}

	def _build_stems(self, words: set[str]) -> set[str]:
		stems = set()

		for word in words:
			stem = self._stem_word(word)

			if stem:
				stems.add(stem)

		return stems

	def _stem_word(self, word: str) -> str:
		if len(word) <= 4:
			return word

		endings = (
			"иями", "ями", "ами",
			"ого", "ему", "ому",
			"ыми", "ими",
			"ией", "иях",
			"ах", "ях",
			"ую", "юю",
			"ая", "яя",
			"ое", "ее",
			"ые", "ие",
			"ый", "ий", "ой",
			"ым", "им",
			"ом", "ем",
			"ся",
			"а", "я", "ы", "и", "у", "ю", "е", "о"
		)

		for ending in endings:
			if word.endswith(ending) and len(word) - len(ending) >= 4:
				return word[:-len(ending)]

		return word

	def _normalize_text(self, text: str) -> str:
		return text.lower().replace("ё", "е")