import re


class ChunkService:
	def split_text(
		self,
		text: str,
		chunk_size: int = 900,
		overlap_size: int = 150
	) -> list[str]:
		normalized_text = self._normalize_text(text)

		if not normalized_text:
			return []

		paragraphs = self._split_into_paragraphs(normalized_text)

		chunks = []
		current_chunk_parts = []
		current_chunk_length = 0

		for paragraph in paragraphs:
			paragraph_parts = self._split_large_text_part(
				text_part=paragraph,
				chunk_size=chunk_size
			)

			for paragraph_part in paragraph_parts:
				paragraph_part_length = len(paragraph_part)

				if paragraph_part_length > chunk_size:
					self._flush_current_chunk(
						chunks=chunks,
						current_chunk_parts=current_chunk_parts
					)

					current_chunk_parts.clear()
					current_chunk_length = 0

					hard_chunks = self._split_by_length(
						text=paragraph_part,
						chunk_size=chunk_size,
						overlap_size=overlap_size
					)

					chunks.extend(hard_chunks)
					continue

				if current_chunk_length + paragraph_part_length + 2 > chunk_size:
					self._flush_current_chunk(
						chunks=chunks,
						current_chunk_parts=current_chunk_parts
					)

					overlap_text = self._build_overlap_text(
						chunks=chunks,
						overlap_size=overlap_size
					)

					current_chunk_parts.clear()

					if overlap_text:
						current_chunk_parts.append(overlap_text)
						current_chunk_length = len(overlap_text)
					else:
						current_chunk_length = 0

				current_chunk_parts.append(paragraph_part)
				current_chunk_length += paragraph_part_length + 2

		self._flush_current_chunk(
			chunks=chunks,
			current_chunk_parts=current_chunk_parts
		)

		return self._remove_duplicate_chunks(chunks)

	def _normalize_text(self, text: str) -> str:
		text = text.replace("\r\n", "\n").replace("\r", "\n")
		text = re.sub(r"[ \t]+", " ", text)
		text = re.sub(r"\n{3,}", "\n\n", text)

		return text.strip()

	def _split_into_paragraphs(self, text: str) -> list[str]:
		paragraphs = re.split(r"\n\s*\n", text)

		return [
			paragraph.strip()
			for paragraph in paragraphs
			if paragraph.strip()
		]

	def _split_large_text_part(self, text_part: str, chunk_size: int) -> list[str]:
		if len(text_part) <= chunk_size:
			return [text_part]

		sentences = self._split_into_sentences(text_part)

		if not sentences:
			return [text_part]

		parts = []
		current_part_sentences = []
		current_part_length = 0

		for sentence in sentences:
			sentence_length = len(sentence)

			if sentence_length > chunk_size:
				if current_part_sentences:
					parts.append(" ".join(current_part_sentences).strip())
					current_part_sentences.clear()
					current_part_length = 0

				parts.append(sentence)
				continue

			if current_part_length + sentence_length + 1 > chunk_size:
				if current_part_sentences:
					parts.append(" ".join(current_part_sentences).strip())

				current_part_sentences = [sentence]
				current_part_length = sentence_length
			else:
				current_part_sentences.append(sentence)
				current_part_length += sentence_length + 1

		if current_part_sentences:
			parts.append(" ".join(current_part_sentences).strip())

		return [
			part
			for part in parts
			if part
		]

	def _split_into_sentences(self, text: str) -> list[str]:
		sentences = re.split(r"(?<=[.!?])\s+", text)

		return [
			sentence.strip()
			for sentence in sentences
			if sentence.strip()
		]

	def _split_by_length(
		self,
		text: str,
		chunk_size: int,
		overlap_size: int
	) -> list[str]:
		chunks = []
		start_position = 0

		while start_position < len(text):
			end_position = start_position + chunk_size
			chunk = text[start_position:end_position].strip()

			if chunk:
				chunks.append(chunk)

			if end_position >= len(text):
				break

			start_position = end_position - overlap_size

			if start_position < 0:
				start_position = 0

		return chunks

	def _flush_current_chunk(
		self,
		chunks: list[str],
		current_chunk_parts: list[str]
	) -> None:
		if not current_chunk_parts:
			return

		chunk = "\n\n".join(current_chunk_parts).strip()

		if chunk:
			chunks.append(chunk)

	def _build_overlap_text(self, chunks: list[str], overlap_size: int) -> str:
		if not chunks or overlap_size <= 0:
			return ""

		last_chunk = chunks[-1]

		if len(last_chunk) <= overlap_size:
			return last_chunk

		overlap_text = last_chunk[-overlap_size:].strip()
		first_space_index = overlap_text.find(" ")

		if first_space_index > 0:
			overlap_text = overlap_text[first_space_index + 1:].strip()

		return overlap_text

	def _remove_duplicate_chunks(self, chunks: list[str]) -> list[str]:
		unique_chunks = []
		seen_chunks = set()

		for chunk in chunks:
			normalized_chunk = re.sub(r"\s+", " ", chunk).strip()

			if not normalized_chunk:
				continue

			if normalized_chunk in seen_chunks:
				continue

			seen_chunks.add(normalized_chunk)
			unique_chunks.append(chunk)

		return unique_chunks