const catImage = document.getElementById("catImage");
const answerText = document.getElementById("answerText");
const questionForm = document.getElementById("questionForm");
const questionInput = document.getElementById("questionInput");
const statusText = document.getElementById("statusText");
const catNoseButton = document.getElementById("catNoseButton");
const catReactionText = document.getElementById("catReactionText");

const catIdleImagePath = "/static/assets/cat_idle.png";
const catTalkingImagePath = "/static/assets/cat_talking.png";
const catAnnoyedImagePath = "/static/assets/cat_annoyed.png";
const catAlertImagePath = "/static/assets/cat_alert.png";

const adminLoginButton = document.getElementById("adminLoginButton");
const adminPanelLink = document.getElementById("adminPanelLink");
const adminLogoutButton = document.getElementById("adminLogoutButton");
const adminLoginModal = document.getElementById("adminLoginModal");
const adminLoginCloseButton = document.getElementById("adminLoginCloseButton");
const adminLoginForm = document.getElementById("adminLoginForm");
const adminUsername = document.getElementById("adminUsername");
const adminPassword = document.getElementById("adminPassword");
const adminLoginError = document.getElementById("adminLoginError");

const adminTokenStorageKey = "molodoy_admin_token";

let typingIntervalId = null;
let mouthAnimationIntervalId = null;
let reactionTimeoutId = null;
let isAnswerTyping = false;

questionForm.addEventListener("submit", async function (event) {
	event.preventDefault();

	const question = questionInput.value.trim();

	if (!question) {
		return;
	}

	questionInput.disabled = true;
	statusText.textContent = "Молодой думает...";
	answerText.textContent = "";
	clearCatReaction();
	catImage.src = catAlertImagePath;

	try {
		const answer = await getAnswerFromBackend(question);

		statusText.textContent = "Молодой отвечает...";
		await typeAnswer(answer);

		statusText.textContent = "Молодой ждёт следующий вопрос.";
	} catch (error) {
		console.error(error);

		stopMouthAnimation();
		catImage.src = catIdleImagePath;

		answerText.textContent = "Что-то пошло не так. Проверь backend или попробуй еще раз.";
		statusText.textContent = "Ошибка ответа.";
	} finally {
		questionInput.disabled = false;
		questionInput.value = "";
		questionInput.focus();
	}
});

async function getAnswerFromBackend(question) {
	const response = await fetch("/chat/ask", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			question: question
		})
	});

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(errorText);
	}

	const result = await response.json();

	return result.answer;
}

function typeAnswer(answer) {
	return new Promise(function (resolve) {
		clearTyping();

		let currentIndex = 0;
		answerText.textContent = "";

		isAnswerTyping = true;
		clearCatReaction();
		startMouthAnimation();

		typingIntervalId = setInterval(function () {
			if (currentIndex >= answer.length) {
				clearTyping();
				stopMouthAnimation();
				isAnswerTyping = false;
				catImage.src = catIdleImagePath;
				resolve();
				return;
			}

			answerText.textContent += answer[currentIndex];
			currentIndex += 1;
		}, 18);
	});
}

function startMouthAnimation() {
	stopMouthAnimation();

	let isTalkingFrame = false;

	mouthAnimationIntervalId = setInterval(function () {
		isTalkingFrame = !isTalkingFrame;

		if (isTalkingFrame) {
			catImage.src = catTalkingImagePath;
		} else {
			catImage.src = catIdleImagePath;
		}
	}, 180);
}

function stopMouthAnimation() {
	if (mouthAnimationIntervalId) {
		clearInterval(mouthAnimationIntervalId);
		mouthAnimationIntervalId = null;
	}
}

function clearTyping() {
	if (typingIntervalId) {
		clearInterval(typingIntervalId);
		typingIntervalId = null;
	}
}

initializeAdminAuth();

function initializeAdminAuth() {
	updateAdminMenuState();

	adminLoginButton.addEventListener("mouseenter", function () {
		showCatReaction(
			catAlertImagePath,
			"Что там шуршит?",
			1200
		);
	});

	adminLoginButton.addEventListener("click", function () {
		openAdminLoginModal();
	});

	adminLoginCloseButton.addEventListener("click", function () {
		closeAdminLoginModal();
	});

	adminLoginModal.addEventListener("click", function (event) {
		if (event.target === adminLoginModal) {
			closeAdminLoginModal();
		}
	});

	adminLoginForm.addEventListener("submit", async function (event) {
		event.preventDefault();

		const username = adminUsername.value.trim();
		const password = adminPassword.value.trim();

		if (!username || !password) {
			showAdminLoginError();
			return;
		}

		await loginAdmin(username, password);
	});

	adminLogoutButton.addEventListener("click", function () {
		localStorage.removeItem(adminTokenStorageKey);
		updateAdminMenuState();
	});
}

async function loginAdmin(username, password) {
	try {
		hideAdminLoginError();

		const response = await fetch("/auth/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				username: username,
				password: password
			})
		});

		if (!response.ok) {
			throw new Error("Invalid credentials");
		}

		const result = await response.json();

		localStorage.setItem(adminTokenStorageKey, result.access_token);

		adminUsername.value = "";
		adminPassword.value = "";

		closeAdminLoginModal();
		updateAdminMenuState();
	} catch (error) {
		console.error(error);
		showAdminLoginError();
	}
}

function openAdminLoginModal() {
	hideAdminLoginError();
	adminLoginModal.classList.remove("is-hidden");
	setTimeout(function () {
		adminUsername.focus();
	}, 50);
}

function closeAdminLoginModal() {
	adminLoginModal.classList.add("is-hidden");
}

function updateAdminMenuState() {
	const token = localStorage.getItem(adminTokenStorageKey);

	if (token) {
		adminPanelLink.classList.remove("is-hidden");
		adminLogoutButton.classList.remove("is-hidden");
		adminLoginButton.classList.add("is-hidden");
	} else {
		adminPanelLink.classList.add("is-hidden");
		adminLogoutButton.classList.add("is-hidden");
		adminLoginButton.classList.remove("is-hidden");
	}
}

function showAdminLoginError() {
	adminLoginError.classList.remove("is-hidden");
}

function hideAdminLoginError() {
	adminLoginError.classList.add("is-hidden");
}

catNoseButton.addEventListener("click", function () {
	showCatReaction(
		catAnnoyedImagePath,
		getRandomPhrase([
			"Эй, хватит.",
			"Нос не кнопка.",
			"Ты сейчас доиграешься.",
			"Лапой по руке дать?",
			"Без фамильярностей, кожаный."
		]),
		1800
	);
});

function showCatReaction(imagePath, phrase, durationMs) {
	if (isAnswerTyping) {
		return;
	}

	clearCatReaction();
	stopMouthAnimation();

	catImage.src = imagePath;
	catReactionText.textContent = phrase;
	catReactionText.classList.remove("is-hidden");

	reactionTimeoutId = setTimeout(function () {
		catImage.src = catIdleImagePath;
		catReactionText.classList.add("is-hidden");
		reactionTimeoutId = null;
	}, durationMs);
}

function clearCatReaction() {
	if (reactionTimeoutId) {
		clearTimeout(reactionTimeoutId);
		reactionTimeoutId = null;
	}

	catReactionText.classList.add("is-hidden");
	catReactionText.textContent = "";
}

function getRandomPhrase(phrases) {
	const index = Math.floor(Math.random() * phrases.length);

	return phrases[index];
}