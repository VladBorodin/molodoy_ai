class AnswerService:
	def build_answer(self, question: str, context_chunks: list[str]) -> str:
		if not context_chunks:
			return (
				"Я не нашел в дневнике Молодого информации, "
				"которая подходит для ответа на этот вопрос."
			)

		context_text = "\n\n".join(context_chunks)

		return (
			"Я нашел информацию, которая может отвечать на вопрос.\n\n"
			f"Вопрос: {question}\n\n"
			f"Найденный контекст:\n{context_text}"
		)