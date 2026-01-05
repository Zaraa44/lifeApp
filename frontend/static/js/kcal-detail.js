document.addEventListener("DOMContentLoaded", async () => {

    const totalEl = document.getElementById("kcal-total");
    const listEl = document.getElementById("kcal-breakdown");

    const res = await fetch("/api/kcal/today");
    const data = await res.json();

    totalEl.textContent = Math.round(data.total_kcal || 0);

    const activities = data.activities || {};

    if (activities.steps) {
        const s = activities.steps;
        addCard(
            "steps",
            "Stappen",
            `${s.steps} stappen · ${s.duration_min} min`,
            s.kcal
        );
    }

    const workouts = activities.workouts || [];
    workouts.forEach((w, i) => {
        addCard(
            "workout",
            w.type || `Workout ${i + 1}`,
            `${w.duration_min} min · MET ${w.met}`,
            w.kcal
        );
    });

    function addCard(type, title, meta, kcal) {
        const card = document.createElement("div");
        card.className = `kcal-card ${type}`;

        card.innerHTML = `
            <div class="kcal-card-left">
                <div class="kcal-card-title">${title}</div>
                <div class="kcal-card-meta">${meta}</div>
            </div>
            <div class="kcal-card-value">
                ${Math.round(kcal)} kcal
            </div>
        `;

        listEl.appendChild(card);
    }
});
