import httpx

from app.settings import settings


class LlmService:
	def generate_answer(
		self,
		system_prompt: str,
		user_message: str
	) -> str:
		self._validate_settings()

		payload = {
			"model": settings.llm_model,
			"messages": [
				{
					"role": "system",
					"content": system_prompt
				},
				{
					"role": "user",
					"content": user_message
				}
			],
			"temperature": settings.llm_temperature,
			"max_tokens": settings.llm_max_tokens
		}

		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {settings.llm_api_key}"
		}

		try:
			with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
				response = client.post(
					settings.llm_api_url,
					headers=headers,
					json=payload
				)

			response.raise_for_status()
		except httpx.HTTPStatusError as error:
			raise RuntimeError(
				f"LLM API returned {error.response.status_code}: {error.response.text}"
			) from error
		except httpx.RequestError as error:
			raise RuntimeError(
				f"LLM API request failed: {str(error)}"
			) from error

		response_data = response.json()

		try:
			answer = response_data["choices"][0]["message"]["content"]
		except (KeyError, IndexError, TypeError) as error:
			raise RuntimeError(
				f"Unexpected LLM API response format: {response_data}"
			) from error

		return answer.strip()

	def _validate_settings(self) -> None:
		if not settings.llm_api_url:
			raise RuntimeError("LLM_API_URL is not configured")

		if not settings.llm_api_key or settings.llm_api_key == "replace_me":
			raise RuntimeError("LLM_API_KEY is not configured")

		if not settings.llm_model:
			raise RuntimeError("LLM_MODEL is not configured")