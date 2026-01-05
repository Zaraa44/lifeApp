document.addEventListener("DOMContentLoaded", () => {

    async function loadKcalToday() {
        try {
            const res = await fetch("/api/kcal/today");
            const data = await res.json();

            const el = document.getElementById("kcal-value");
            if (!el) return;

            el.textContent = Math.round(data.total_kcal || 0);
        } catch {
        }
    }

    loadKcalToday();
});
const kcalCard = document.getElementById("kcal-card");
if (kcalCard) {
    kcalCard.addEventListener("click", () => {
        window.location.href = "/kcal";
    });
}
