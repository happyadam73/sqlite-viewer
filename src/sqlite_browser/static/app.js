(() => {
  const root = document.documentElement;
  const themeToggle = document.querySelector('[data-testid="theme-toggle"]');
  const fileInput = document.getElementById("db-file-input");
  const openFileButtons = document.querySelectorAll('[data-action="open-file"]');
  const errorBanner = document.querySelector('[data-testid="error-banner"]');
  const storageKey = "sqlite-browser-theme";

  function applyTheme(choice) {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const resolvedTheme = choice === "system" ? (prefersDark ? "dark" : "light") : choice;
    root.dataset.theme = resolvedTheme;
    if (themeToggle instanceof HTMLButtonElement) {
      themeToggle.dataset.themeChoice = choice;
      themeToggle.setAttribute("aria-pressed", resolvedTheme === "dark" ? "true" : "false");
      themeToggle.textContent = resolvedTheme === "dark" ? "Switch to light theme" : "Switch to dark theme";
    }
  }

  function showBanner(message) {
    if (!(errorBanner instanceof HTMLElement)) {
      return;
    }

    errorBanner.hidden = false;
    errorBanner.textContent = message;
  }

  const savedTheme = window.localStorage.getItem(storageKey) ?? "system";
  applyTheme(savedTheme);

  themeToggle?.addEventListener("click", () => {
    const currentChoice = themeToggle.dataset.themeChoice ?? "system";
    const nextChoice = currentChoice === "dark" ? "light" : "dark";
    window.localStorage.setItem(storageKey, nextChoice);
    applyTheme(nextChoice);
  });

  openFileButtons.forEach((button) => {
    button.addEventListener("click", () => {
      fileInput?.click();
    });
  });

  fileInput?.addEventListener("change", () => {
    if (fileInput.files?.length) {
      fileInput.value = "";
      showBanner("Browser upload will be connected in a later milestone. The shell is ready for it.");
    }
  });
})();
