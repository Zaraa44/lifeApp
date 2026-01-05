document.addEventListener("DOMContentLoaded", () => {

    async function loadWeight() {
        const res = await fetch("/api/weight");
        const data = await res.json();

        if (data && data.weight) {
            document.getElementById("weight-value").textContent =
                data.weight.toFixed(1);
        }
    }

    const weightCard = document.getElementById("weight-card");
    const modal = document.getElementById("weight-modal");
    const saveBtn = document.getElementById("save-weight");
    const input = document.getElementById("weight-input");

    weightCard.addEventListener("click", () => {
        modal.classList.remove("hidden");
        input.focus();
    });

    saveBtn.addEventListener("click", async () => {
        const value = parseFloat(input.value);
        if (!value) return;

        await fetch("/api/weight", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ weight: value })
        });

        input.value = "";
        modal.classList.add("hidden");
        loadWeight();
    });

    loadWeight();
});
