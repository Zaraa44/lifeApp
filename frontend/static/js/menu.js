

document.getElementById("menuBtn")
    .addEventListener("click", () => {
        window.location.href = "/profile";
    });

const workoutBtn = document.getElementById("workoutBtn");
if (workoutBtn) {
    workoutBtn.addEventListener("click", () => {
        window.location.href = "/workout";
    });
}
