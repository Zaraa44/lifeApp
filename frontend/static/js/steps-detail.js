document.addEventListener("DOMContentLoaded", async () => {

    const GOAL = 8000;

    const stepsCountEl = document.getElementById("steps-count");
    const stepsGoalEl = document.getElementById("steps-goal");
    const ringEl = document.getElementById("ring-progress");
    const historyEl = document.getElementById("steps-history");
    const chartEl = document.getElementById("steps-bar-chart");

    const todayRes = await fetch("/api/steps");
    const today = await todayRes.json();
    const stepsToday = today.steps;

    stepsCountEl.textContent = stepsToday;
    stepsGoalEl.textContent = GOAL;

    const circumference = 326;
    const progress = Math.min(stepsToday / GOAL, 1);

    ringEl.style.strokeDashoffset =
        circumference * (1 - progress);

    const histRes = await fetch("/api/steps/history");
    const history = await histRes.json();

    historyEl.innerHTML = "";

    history
        .slice()
        .reverse()
        .forEach(day => {
            const row = document.createElement("div");
            row.className = "steps-day";
            row.innerHTML = `
                <span>${day.date}</span>
                <span>${day.steps} stappen</span>
            `;
            historyEl.appendChild(row);
        });

    chartEl.innerHTML = "";

    const allDays = [
        ...history,
        {
            date: today.date,
            steps: stepsToday
        }
    ];

    const last7 = allDays.slice(-7);

    const maxSteps = Math.max(
        GOAL,
        ...last7.map(d => d.steps)
    );

  last7.forEach(d => {
    const heightPct = Math.min(d.steps / GOAL, 1);

    const bar = document.createElement("div");
    bar.className = "steps-bar";

    bar.innerHTML = `
        <div class="steps-bar-rect"
             style="height:${Math.max(heightPct, 0.05) * 100}%"></div>
        <div class="steps-bar-label">
            ${d.date.slice(5)}
        </div>
    `;

    chartEl.appendChild(bar);
});


});
