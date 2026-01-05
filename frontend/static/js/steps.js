async function loadSteps() {
    try {
        const res = await fetch("/api/steps");

        if (res.redirected) {
            window.location.href = res.url;
            return;
        }

        if (!res.ok) {
            throw new Error("API error");
        }

        const data = await res.json();

        const stepsEl = document.getElementById("steps-value");
        if (stepsEl) {
            const steps = data.steps;

stepsEl.textContent = steps.toLocaleString("nl-NL");

const km = (steps * 0.75) / 1000;

const kmEl = document.getElementById("steps-km");
if (kmEl) {
    kmEl.textContent = `${km.toFixed(2)} km`;
}

        }
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener("DOMContentLoaded", loadSteps);