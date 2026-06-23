const adminTokenStorageKey = "molodoy_admin_token";
const adminToken = localStorage.getItem(adminTokenStorageKey);

if (!adminToken) {
	alert("Нужно войти как администратор.");
	window.location.href = "/";
}

const entryForm = document.getElementById("entryForm");
const entryTitle = document.getElementById("entryTitle");
const entryContent = document.getElementById("entryContent");
const entryIsActive = document.getElementById("entryIsActive");

const saveButton = document.getElementById("saveButton");
const clearButton = document.getElementById("clearButton");
const newEntryButton = document.getElementById("newEntryButton");
const reloadEntriesButton = document.getElementById("reloadEntriesButton");
const logoutButton = document.getElementById("logoutButton");

const formTitle = document.getElementById("formTitle");
const adminStatusText = document.getElementById("adminStatusText");
const adminResult = document.getElementById("adminResult");
const resultEntryId = document.getElementById("resultEntryId");
const resultChunksCount = document.getElementById("resultChunksCount");
const entriesList = document.getElementById("entriesList");

let editingEntryId = null;

initializeAdminPage();

function initializeAdminPage() {
	entryForm.addEventListener("submit", handleEntryFormSubmit);
	clearButton.addEventListener("click", resetForm);
	newEntryButton.addEventListener("click", resetForm);
	reloadEntriesButton.addEventListener("click", loadEntries);
	logoutButton.addEventListener("click", logoutAdmin);

	loadEntries();
}

async function handleEntryFormSubmit(event) {
	event.preventDefault();

	const title = entryTitle.value.trim();
	const content = entryContent.value.trim();
	const isActive = entryIsActive.checked;

	if (!title || !content) {
		showStatus("Заполни название и текст записи.", "error");
		return;
	}

	if (editingEntryId) {
		await updateKnowledgeEntry(editingEntryId, title, content, isActive);
	} else {
		await createKnowledgeEntry(title, content);
	}
}

async function loadEntries() {
	try {
		entriesList.innerHTML = `<p class="empty-list-text">Загружаю записи...</p>`;

		const response = await fetch("/admin/entries", {
			method: "GET",
			headers: getAdminHeaders()
		});

		if (!response.ok) {
			await handleBadResponse(response);
			return;
		}

		const entries = await response.json();

		renderEntries(entries);
	} catch (error) {
		console.error(error);
		entriesList.innerHTML = `<p class="empty-list-text">Не удалось загрузить записи.</p>`;
		showStatus("Не удалось загрузить список записей.", "error");
	}
}

function renderEntries(entries) {
	if (!entries.length) {
		entriesList.innerHTML = `<p class="empty-list-text">Пока нет записей.</p>`;
		return;
	}

	entriesList.innerHTML = "";

	for (const entry of entries) {
		const entryElement = document.createElement("article");
		entryElement.className = "entry-item";

		if (entry.id === editingEntryId) {
			entryElement.classList.add("is-selected");
		}

		const statusText = entry.is_active ? "Активна" : "Отключена";
		const updatedAt = entry.updated_at ? formatDate(entry.updated_at) : "—";

		entryElement.innerHTML = `
			<div class="entry-item-header">
				<h3>${escapeHtml(entry.title)}</h3>
				<span class="entry-status ${entry.is_active ? "entry-status-active" : "entry-status-inactive"}">
					${statusText}
				</span>
			</div>

			<p class="entry-preview">
				${escapeHtml(entry.content_preview)}
			</p>

			<div class="entry-meta">
				<span>ID: ${entry.id}</span>
				<span>Чанков: ${entry.chunks_count}</span>
				<span>Создано: ${formatDate(entry.created_at)}</span>
				<span>Обновлено: ${updatedAt}</span>
			</div>

			<div class="entry-actions">
				<button type="button" data-action="edit" data-entry-id="${entry.id}">
					Редактировать
				</button>

				<button type="button" class="danger-button" data-action="delete" data-entry-id="${entry.id}" data-entry-title="${escapeHtml(entry.title)}">
					Удалить
				</button>
			</div>
		`;

		entryElement.addEventListener("click", handleEntryItemClick);

		entriesList.appendChild(entryElement);
	}
}

async function handleEntryItemClick(event) {
	const button = event.target.closest("button");

	if (!button) {
		return;
	}

	const action = button.dataset.action;
	const entryId = Number(button.dataset.entryId);

	if (action === "edit") {
		await loadEntryForEdit(entryId);
	}

	if (action === "delete") {
		const entryTitle = button.dataset.entryTitle || "эту запись";
		await deleteKnowledgeEntry(entryId, entryTitle);
	}
}

async function loadEntryForEdit(entryId) {
	try {
		showStatus("Загружаю запись для редактирования...", "default");

		const response = await fetch(`/admin/entries/${entryId}`, {
			method: "GET",
			headers: getAdminHeaders()
		});

		if (!response.ok) {
			await handleBadResponse(response);
			return;
		}

		const entry = await response.json();

		editingEntryId = entry.id;
		entryTitle.value = entry.title;
		entryContent.value = entry.content;
		entryIsActive.checked = entry.is_active;

		formTitle.textContent = `Редактирование #${entry.id}`;
		saveButton.textContent = "Обновить запись";

		adminResult.classList.add("is-hidden");

		showStatus("Запись загружена. Можно редактировать.", "success");

		window.scrollTo({
			top: 0,
			behavior: "smooth"
		});

		await loadEntries();
	} catch (error) {
		console.error(error);
		showStatus("Не удалось открыть запись для редактирования.", "error");
	}
}

async function createKnowledgeEntry(title, content) {
	try {
		setLoadingState(true);
		showStatus("Сохраняю новую запись...", "default");

		const response = await fetch("/admin/entries", {
			method: "POST",
			headers: getAdminHeaders(),
			body: JSON.stringify({
				title: title,
				content: content
			})
		});

		if (!response.ok) {
			await handleBadResponse(response);
			return;
		}

		const result = await response.json();

		showResult(result.entry_id, result.chunks_count);
		showStatus("Запись успешно создана.", "success");

		resetForm(false);
		await loadEntries();
	} catch (error) {
		console.error(error);
		showStatus("Не удалось создать запись.", "error");
	} finally {
		setLoadingState(false);
	}
}

async function updateKnowledgeEntry(entryId, title, content, isActive) {
	try {
		setLoadingState(true);
		showStatus("Обновляю запись и пересобираю чанки...", "default");

		const response = await fetch(`/admin/entries/${entryId}`, {
			method: "PUT",
			headers: getAdminHeaders(),
			body: JSON.stringify({
				title: title,
				content: content,
				is_active: isActive
			})
		});

		if (!response.ok) {
			await handleBadResponse(response);
			return;
		}

		const result = await response.json();

		showResult(result.entry_id, result.chunks_count);
		showStatus("Запись успешно обновлена.", "success");

		resetForm(false);
		await loadEntries();
	} catch (error) {
		console.error(error);
		showStatus("Не удалось обновить запись.", "error");
	} finally {
		setLoadingState(false);
	}
}

async function deleteKnowledgeEntry(entryId, entryTitleText) {
	const isConfirmed = confirm(`Точно удалить запись "${entryTitleText}"?`);

	if (!isConfirmed) {
		return;
	}

	try {
		showStatus("Удаляю запись...", "default");

		const response = await fetch(`/admin/entries/${entryId}`, {
			method: "DELETE",
			headers: getAdminHeaders()
		});

		if (!response.ok) {
			await handleBadResponse(response);
			return;
		}

		const result = await response.json();

		if (editingEntryId === result.deleted_entry_id) {
			resetForm(false);
		}

		showStatus(`Запись #${result.deleted_entry_id} удалена.`, "success");
		adminResult.classList.add("is-hidden");

		await loadEntries();
	} catch (error) {
		console.error(error);
		showStatus("Не удалось удалить запись.", "error");
	}
}

function resetForm(showMessage = true) {
	editingEntryId = null;

	entryTitle.value = "";
	entryContent.value = "";
	entryIsActive.checked = true;

	formTitle.textContent = "Новая запись";
	saveButton.textContent = "Сохранить запись";

	adminResult.classList.add("is-hidden");

	if (showMessage) {
		showStatus("Форма очищена.", "default");
	}

	entryTitle.focus();

	loadEntries();
}

function showResult(entryId, chunksCount) {
	resultEntryId.textContent = entryId;
	resultChunksCount.textContent = chunksCount;
	adminResult.classList.remove("is-hidden");
}

function setLoadingState(isLoading) {
	saveButton.disabled = isLoading;
	clearButton.disabled = isLoading;
	newEntryButton.disabled = isLoading;
	reloadEntriesButton.disabled = isLoading;

	if (isLoading) {
		saveButton.textContent = editingEntryId ? "Обновляю..." : "Сохраняю...";
	} else {
		saveButton.textContent = editingEntryId ? "Обновить запись" : "Сохранить запись";
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

function getAdminHeaders() {
	return {
		"Content-Type": "application/json",
		"Authorization": "Bearer " + adminToken
	};
}

async function handleBadResponse(response) {
	if (response.status === 401 || response.status === 403) {
		localStorage.removeItem(adminTokenStorageKey);
		alert("Сессия администратора истекла. Войдите снова.");
		window.location.href = "/";
		return;
	}

	const errorText = await response.text();
	throw new Error(errorText);
}

function logoutAdmin() {
	localStorage.removeItem(adminTokenStorageKey);
	window.location.href = "/";
}

function formatDate(value) {
	if (!value) {
		return "—";
	}

	const date = new Date(value);

	if (Number.isNaN(date.getTime())) {
		return "—";
	}

	return date.toLocaleString("ru-RU", {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit"
	});
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}