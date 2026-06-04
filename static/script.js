const catImage = document.getElementById("catImage");
const answerText = document.getElementById("answerText");
const questionForm = document.getElementById("questionForm");
const questionInput = document.getElementById("questionInput");
const statusText = document.getElementById("statusText");

const catIdleImagePath = "/static/assets/cat_idle.png";
const catTalkingImagePath = "/static/assets/cat_talking.png";

questionForm.addEventListener("submit", async function (event) {
	event.preventDefault();

	const question = questionInput.value.trim();

	if (!question) {
		return;
	}

	statusText.textContent = "Молодой думает...";
	catImage.src = catTalkingImagePath;

	answerText.textContent = "Мяу. Я получил вопрос: " + question;

	setTimeout(function () {
		catImage.src = catIdleImagePath;
		statusText.textContent = "Молодой ждёт следующий вопрос.";
	}, 1200);
});