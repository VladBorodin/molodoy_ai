const entryForm = document.getElementById("entryForm");
const entryTitle = document.getElementById("entryTitle");
const entryContent = document.getElementById("entryContent");
const saveButton = document.getElementById("saveButton");
const clearButton = document.getElementById("clearButton");
const adminStatusText = document.getElementById("adminStatusText");
const adminResult = document.getElementById("adminResult");
const resultEntryId = document.getElementById("resultEntryId");
const resultChunksCount = document.getElementById("resultChunksCount");

entryForm.addEventListener("submit", async function (event) {
	event.preventDefault();

	const title = entryTitle.value.trim();
	const content = entryContent.value.trim();

	if (!title || !content) {
		showStatus("Заполни название и текст записи.", "error");
		return;
	}

	await createKnowledgeEntry(title, content);
});

clearButton.addEventListener("click", function () {
	entryTitle.value = "";
	entryContent.value = "";
	adminResult.classList.add("is-hidden");
	showStatus("Форма очищена.", "default");
	entryTitle.focus();
});

async function createKnowledgeEntry(title, content) {
	try {
		setLoadingState(true);
		showStatus("Сохраняю запись...", "default");

		const response = await fetch("/admin/entries", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				title: title,
				content: content
			})
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(errorText);
		}

		const result = await response.json();

		resultEntryId.textContent = result.entry_id;
		resultChunksCount.textContent = result.chunks_count;
		adminResult.classList.remove("is-hidden");

		showStatus("Запись успешно сохранена.", "success");
	} catch (error) {
		console.error(error);
		showStatus("Не удалось сохранить запись. Проверь backend или Swagger.", "error");
	} finally {
		setLoadingState(false);
	}
}

function setLoadingState(isLoading) {
	saveButton.disabled = isLoading;
	clearButton.disabled = isLoading;

	if (isLoading) {
		saveButton.textContent = "Сохраняю...";
	} else {
		saveButton.textContent = "Сохранить запись";
	}
}

function showStatus(message, type) {
	adminStatusText.textContent = message;

	adminStatusText.classList.remove(
		"admin-status-success",
		"admin-status-error"
	);

	if (type === "success") {
		adminStatusText.classList.add("admin-status-success");
	}

	if (type === "error") {
		adminStatusText.classList.add("admin-status-error");
	}
}