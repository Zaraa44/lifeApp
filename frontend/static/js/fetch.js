fetch("/api/steps")
  .then(res => res.json())
  .then(data => {
      const today = data[data.length - 1];
      document.querySelector("#steps-value").textContent = today.steps;
  });