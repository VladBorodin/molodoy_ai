const catImage = document.getElementById("catImage");
const answerText = document.getElementById("answerText");
const questionForm = document.getElementById("questionForm");
const questionInput = document.getElementById("questionInput");
const statusText = document.getElementById("statusText");

const catIdleImagePath = "/static/assets/cat_idle.png";
const catTalkingImagePath = "/static/assets/cat_talking.png";

let typingIntervalId = null;
let mouthAnimationIntervalId = null;

questionForm.addEventListener("submit", async function (event) {
	event.preventDefault();

	const question = questionInput.value.trim();

	if (!question) {
		return;
	}

	questionInput.disabled = true;
	statusText.textContent = "Молодой думает...";
	answerText.textContent = "";

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

		startMouthAnimation();

		typingIntervalId = setInterval(function () {
			if (currentIndex >= answer.length) {
				clearTyping();
				stopMouthAnimation();
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