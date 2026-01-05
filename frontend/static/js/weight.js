document.addEventListener("DOMContentLoaded", () => {


    async function loadWeight() {
        const res = await fetch("/api/weight");
        const data = await res.json();

        if (data && data.weight) {
            document.getElementById("weight-value").textContent =
                data.weight.toFixed(1);
        }
    }


    async function loadWeightChart() {
    const res = await fetch("/api/weight/all");
    const data = await res.json();

    if (!data || data.length < 2) return;

    const startWeight = data[0].weight;
    const deltas = data.map(d => d.weight - startWeight);
    const dates = data.map(d => new Date(d.timestamp));

    const svg = document.getElementById("weight-chart");
    if (!svg) return;
    svg.innerHTML = "";

    const width = 300;
    const height = 120;
    const padding = 18;
    const ns = "http://www.w3.org/2000/svg";

    const min = Math.min(...deltas);
    const max = Math.max(...deltas);
    const range = max - min || 1;

    const xAxis = document.createElementNS(ns, "line");
    xAxis.setAttribute("x1", padding);
    xAxis.setAttribute("y1", height - padding);
    xAxis.setAttribute("x2", width - padding);
    xAxis.setAttribute("y2", height - padding);
    xAxis.setAttribute("class", "chart-axis");
    svg.appendChild(xAxis);

    const yAxis = document.createElementNS(ns, "line");
    yAxis.setAttribute("x1", padding);
    yAxis.setAttribute("y1", padding);
    yAxis.setAttribute("x2", padding);
    yAxis.setAttribute("y2", height - padding);
    yAxis.setAttribute("class", "chart-axis");
    svg.appendChild(yAxis);

    const points = deltas.map((v, i) => {
        const x = padding + (i / (deltas.length - 1)) * (width - padding * 2);
        const y = height - padding - ((v - min) / range) * (height - padding * 2);
        return `${x},${y}`;
    });

    const polyline = document.createElementNS(ns, "polyline");
    polyline.setAttribute("points", points.join(" "));
    polyline.setAttribute("class", "chart-line");
    svg.appendChild(polyline);

    const [cx, cy] = points[points.length - 1].split(",");
    const dot = document.createElementNS(ns, "circle");
    dot.setAttribute("cx", cx);
    dot.setAttribute("cy", cy);
    dot.setAttribute("r", 3);
    dot.setAttribute("class", "chart-dot");
    svg.appendChild(dot);


    const formatDate = d =>
        d.toLocaleDateString("nl-NL", { day: "2-digit", month: "2-digit" });

    const startLabel = document.createElementNS(ns, "text");
    startLabel.setAttribute("x", padding);
    startLabel.setAttribute("y", height - 4);
    startLabel.setAttribute("class", "chart-label");
    startLabel.textContent = formatDate(dates[0]);
    svg.appendChild(startLabel);

    const endLabel = document.createElementNS(ns, "text");
    endLabel.setAttribute("x", width - padding);
    endLabel.setAttribute("y", height - 4);
    endLabel.setAttribute("text-anchor", "end");
    endLabel.setAttribute("class", "chart-label");
    endLabel.textContent = formatDate(dates[dates.length - 1]);
    svg.appendChild(endLabel);


const maxWeight = startWeight + max;
const minWeight = startWeight + min;

const labelX = -15;

const maxLabel = document.createElementNS(ns, "text");
maxLabel.setAttribute("x", labelX);
maxLabel.setAttribute("y", padding + 4);
maxLabel.setAttribute("class", "chart-label");
maxLabel.setAttribute("text-anchor", "start");
maxLabel.textContent = `${maxWeight.toFixed(1)} kg`;
svg.appendChild(maxLabel);

const minLabel = document.createElementNS(ns, "text");
minLabel.setAttribute("x", labelX);
minLabel.setAttribute("y", height - padding);
minLabel.setAttribute("class", "chart-label");
minLabel.setAttribute("text-anchor", "start");
minLabel.textContent = `${minWeight.toFixed(1)} kg`;
svg.appendChild(minLabel);

    const delta = deltas[deltas.length - 1];
    const sign = delta < 0 ? "" : "+";
    const deltaEl = document.getElementById("weight-delta");

    if (deltaEl) {
        deltaEl.textContent = `${sign}${delta.toFixed(1)} kg sinds start`;
    }
}


    const weightCard = document.getElementById("weight-card");
    const modal = document.getElementById("weight-modal");
    const saveBtn = document.getElementById("save-weight");
    const input = document.getElementById("weight-input");

    if (weightCard && modal && saveBtn && input) {

        weightCard.addEventListener("click", () => {
            modal.classList.remove("hidden");
            input.focus();
        });

        saveBtn.addEventListener("click", async () => {
            let raw = input.value.trim();
            if (!raw) return;

            raw = raw.replace(",", ".");
            const value = Number(raw);

            if (Number.isNaN(value)) {
                alert("Vul een geldig gewicht in (bijv. 72,4)");
                return;
            }

            await fetch("/api/weight", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ weight: value })
            });

            input.value = "";
            modal.classList.add("hidden");

            loadWeight();
            loadWeightChart();
        });
    }

    loadWeight();
    loadWeightChart();

});
