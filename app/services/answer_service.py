from app.settings import settings
from app.services.llm_service import LlmService
from app.services.search_service import SearchResult


class AnswerService:
	def __init__(self, llm_service: LlmService | None = None):
		self.llm_service = llm_service or LlmService()

	def build_answer(
		self,
		question: str,
		search_results: list[SearchResult]
	) -> str:
		if not search_results:
			return (
				"Я не нашёл в дневнике Молодого информации, "
				"которая подходит для ответа на этот вопрос."
			)

		system_prompt = self._build_system_prompt()
		user_message = self._build_user_message(
			question=question,
			search_results=search_results
		)

		try:
			return self.llm_service.generate_answer(
				system_prompt=system_prompt,
				user_message=user_message
			)
		except RuntimeError as error:
			return (
				"Я нашёл подходящие записи в дневнике, но сейчас не смог получить ответ от ИИ. "
				f"Техническая ошибка: {str(error)}"
			)

	def _build_system_prompt(self) -> str:
		return (
			"Ты — локальный ИИ-помощник проекта Molodoy AI. "
			"Ты отвечаешь на вопросы о коте по имени Молодой. "
			"Отвечай только на основании предоставленного контекста из дневниковых записей. "
			"Не выдумывай факты, даты, события и подробности, которых нет в контексте. "
			"Если в контексте нет ответа, честно скажи, что в дневнике нет такой информации. "
			"Отвечай по-русски, естественно, кратко и понятно. "
			"Можно сохранять лёгкий ироничный стиль, но без потери смысла."
		)

	def _build_user_message(
		self,
		question: str,
		search_results: list[SearchResult]
	) -> str:
		context = self._build_context(search_results)

		return (
			"Контекст из дневника Молодого:\n"
			f"{context}\n\n"
			"Вопрос пользователя:\n"
			f"{question}\n\n"
			"Сформируй ответ только на основании контекста."
		)

	def _build_context(self, search_results: list[SearchResult]) -> str:
		context_parts = []
		current_length = 0

		for index, result in enumerate(search_results, start=1):
			part = (
				f"[Источник {index}]\n"
				f"Название записи: {result.entry_title}\n"
				f"ID записи: {result.entry_id}\n"
				f"Позиция чанка: {result.position}\n"
				f"Текст:\n{result.content}"
			)

			if current_length + len(part) > settings.rag_max_context_chars:
				break

			context_parts.append(part)
			current_length += len(part)

		return "\n\n---\n\n".join(context_parts)