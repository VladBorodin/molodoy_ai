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
	def __init__(self):
		self.stop_words = {
			"что", "как", "где", "когда", "куда", "откуда", "зачем", "почему",
			"какой", "какая", "какое", "какие",
			"это", "есть", "был", "была", "были", "будет",
			"про", "для", "или", "его", "она", "оно", "они",
			"кот", "кота", "коту", "котом",
			"молодой", "молодого", "молодому", "молодым"
		}

	def find_relevant_chunks(
		self,
		question: str,
		chunks: list[KnowledgeChunk],
		limit: int | None = None
	) -> list[SearchResult]:
		limit = limit or settings.rag_max_context_chunks

		question_words = self._extract_meaningful_words(question)

		if not question_words:
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
				SearchResult(
					chunk_id=chunk.id,
					entry_id=chunk.entry_id,
					entry_title=entry_title,
					position=chunk.position,
					content=chunk.content,
					score=score
				)
			)

		results.sort(key=lambda item: item.score, reverse=True)

		return results[:limit]

	def _calculate_score(
		self,
		question_words: set[str],
		chunk_content: str,
		entry_title: str
	) -> int:
		chunk_words = self._extract_words(chunk_content)
		title_words = self._extract_words(entry_title)

		matched_chunk_words = question_words.intersection(chunk_words)
		matched_title_words = question_words.intersection(title_words)

		score = 0

		score += len(matched_chunk_words) * 10
		score += len(matched_title_words) * 5

		normalized_chunk = self._normalize_text(chunk_content)
		normalized_title = self._normalize_text(entry_title)

		for word in question_words:
			if word in normalized_chunk:
				score += 2

			if word in normalized_title:
				score += 3

		return score

	def _extract_meaningful_words(self, text: str) -> set[str]:
		words = self._extract_words(text)

		return {
			word
			for word in words
			if word not in self.stop_words
		}

	def _extract_words(self, text: str) -> set[str]:
		normalized_text = self._normalize_text(text)
		words = re.findall(r"[а-яa-z0-9]+", normalized_text)

		return {
			word
			for word in words
			if len(word) > 2
		}

	def _normalize_text(self, text: str) -> str:
		return text.lower().replace("ё", "е")