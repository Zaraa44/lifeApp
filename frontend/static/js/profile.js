document.addEventListener("DOMContentLoaded", () => {

    const sex = document.getElementById("profile-sex");
    const age = document.getElementById("profile-age");
    const height = document.getElementById("profile-height");
    const save = document.getElementById("save-profile");

    async function loadProfile() {
        const res = await fetch("/api/profile");
        const data = await res.json();

        if (!data) return;

        sex.value = data.sex || "";
        age.value = data.age || "";
        height.value = data.height_cm || "";
    }

    save.addEventListener("click", async () => {
        const payload = {
            sex: sex.value,
            age: age.value,
            height_cm: height.value
        };

        await fetch("/api/profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        window.history.back();
    });

    loadProfile();
});
async function loadGoogleStatus() {
    const res = await fetch("/api/google/status");
    const data = await res.json();

    const statusEl = document.getElementById("google-status");
    const btn = document.getElementById("google-connect");

    if (data.connected) {
        statusEl.textContent = "Google Fit gekoppeld";
        btn.textContent = "Opnieuw koppelen";
    } else {
        statusEl.textContent = "Niet gekoppeld";
        btn.textContent = "Koppel Google Fit";
    }
}

document.getElementById("google-connect")
    .addEventListener("click", () => {
        window.location.href = "/auth/login";
    });

loadGoogleStatus();
