import re


class ChunkService:
	def split_text(
		self,
		text: str,
		chunk_size: int = 900,
		overlap_sentences: int = 1,
		max_overlap_length: int = 220
	) -> list[str]:
		normalized_text = self._normalize_text(text)

		if not normalized_text:
			return []

		text_units = self._split_text_to_units(
			text=normalized_text,
			chunk_size=chunk_size
		)

		chunks = []
		current_units = []

		for text_unit in text_units:
			text_unit = text_unit.strip()

			if not text_unit:
				continue

			if len(text_unit) > chunk_size:
				self._flush_current_chunk(chunks, current_units)
				current_units.clear()

				long_parts = self._split_long_unit_by_words(
					text_unit=text_unit,
					chunk_size=chunk_size
				)

				chunks.extend(long_parts)
				continue

			candidate_units = current_units + [text_unit]
			candidate_text = self._join_units(candidate_units)

			if current_units and len(candidate_text) > chunk_size:
				self._flush_current_chunk(chunks, current_units)

				current_units = self._build_sentence_overlap(
					source_units=current_units,
					overlap_sentences=overlap_sentences,
					max_overlap_length=max_overlap_length
				)

				candidate_with_overlap = self._join_units(current_units + [text_unit])

				if len(candidate_with_overlap) > chunk_size:
					current_units.clear()

			current_units.append(text_unit)

		self._flush_current_chunk(chunks, current_units)

		unique_chunks = self._remove_duplicate_chunks(chunks)

		return self._merge_small_tail_chunk(
			chunks=unique_chunks,
			chunk_size=chunk_size,
			min_tail_length=300,
			max_extra_length=200
		)

	def _normalize_text(self, text: str) -> str:
		text = text.replace("\r\n", "\n").replace("\r", "\n")
		text = re.sub(r"[ \t]+", " ", text)
		text = re.sub(r"\n{3,}", "\n\n", text)

		return text.strip()

	def _split_text_to_units(self, text: str, chunk_size: int) -> list[str]:
		paragraphs = self._split_into_paragraphs(text)
		text_units = []

		for paragraph in paragraphs:
			sentences = self._split_into_sentences(paragraph)

			if not sentences:
				continue

			for sentence in sentences:
				if len(sentence) <= chunk_size:
					text_units.append(sentence)
				else:
					text_units.extend(
						self._split_long_unit_by_words(
							text_unit=sentence,
							chunk_size=chunk_size
						)
					)

		return text_units

	def _split_into_paragraphs(self, text: str) -> list[str]:
		paragraphs = re.split(r"\n\s*\n", text)

		return [
			paragraph.strip()
			for paragraph in paragraphs
			if paragraph.strip()
		]

	def _split_into_sentences(self, text: str) -> list[str]:
		sentences = re.split(r"(?<=[.!?…])\s+", text)

		return [
			sentence.strip()
			for sentence in sentences
			if sentence.strip()
		]

	def _split_long_unit_by_words(self, text_unit: str, chunk_size: int) -> list[str]:
		words = text_unit.split()

		if not words:
			return []

		parts = []
		current_words = []

		for word in words:
			if len(word) > chunk_size:
				if current_words:
					parts.append(" ".join(current_words).strip())
					current_words.clear()

				parts.extend(self._split_very_long_word(word, chunk_size))
				continue

			candidate_words = current_words + [word]
			candidate_text = " ".join(candidate_words)

			if current_words and len(candidate_text) > chunk_size:
				parts.append(" ".join(current_words).strip())
				current_words = [word]
			else:
				current_words.append(word)

		if current_words:
			parts.append(" ".join(current_words).strip())

		return [
			part
			for part in parts
			if part
		]

	def _split_very_long_word(self, word: str, chunk_size: int) -> list[str]:
		parts = []

		for start_position in range(0, len(word), chunk_size):
			part = word[start_position:start_position + chunk_size].strip()

			if part:
				parts.append(part)

		return parts

	def _build_sentence_overlap(
		self,
		source_units: list[str],
		overlap_sentences: int,
		max_overlap_length: int
	) -> list[str]:
		if overlap_sentences <= 0 or max_overlap_length <= 0:
			return []

		overlap_units = []

		for source_unit in reversed(source_units):
			if not self._looks_like_complete_sentence(source_unit):
				continue

			candidate_units = [source_unit] + overlap_units
			candidate_text = self._join_units(candidate_units)

			if len(candidate_text) > max_overlap_length:
				break

			overlap_units.insert(0, source_unit)

			if len(overlap_units) >= overlap_sentences:
				break

		return overlap_units

	def _looks_like_complete_sentence(self, text: str) -> bool:
		cleaned_text = text.strip().rstrip("»”\"')]}")

		return cleaned_text.endswith((".", "!", "?", "…"))

	def _flush_current_chunk(
		self,
		chunks: list[str],
		current_units: list[str]
	) -> None:
		if not current_units:
			return

		chunk = self._join_units(current_units)

		if chunk:
			chunks.append(chunk)

	def _join_units(self, units: list[str]) -> str:
		return " ".join(
			unit.strip()
			for unit in units
			if unit.strip()
		).strip()

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
			unique_chunks.append(normalized_chunk)

		return unique_chunks
	
	def _merge_small_tail_chunk(
		self,
		chunks: list[str],
		chunk_size: int,
		min_tail_length: int,
		max_extra_length: int
	) -> list[str]:
		if len(chunks) < 2:
			return chunks

		last_chunk = chunks[-1]
		previous_chunk = chunks[-2]

		if len(last_chunk) >= min_tail_length:
			return chunks

		tail_without_overlap = self._remove_repeated_prefix(
			previous_chunk=previous_chunk,
			last_chunk=last_chunk
		)

		if not tail_without_overlap:
			return chunks[:-1]

		merged_chunk = f"{previous_chunk} {tail_without_overlap}".strip()
		max_allowed_length = chunk_size + max_extra_length

		if len(merged_chunk) <= max_allowed_length:
			return chunks[:-2] + [merged_chunk]

		return chunks

	def _remove_repeated_prefix(
		self,
		previous_chunk: str,
		last_chunk: str
	) -> str:
		previous_sentences = set(self._split_into_sentences(previous_chunk))
		last_sentences = self._split_into_sentences(last_chunk)

		clean_sentences = []

		for sentence in last_sentences:
			if not clean_sentences and sentence in previous_sentences:
				continue

			clean_sentences.append(sentence)

		return " ".join(clean_sentences).strip()