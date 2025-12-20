// theme.js
document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    root.classList.add("dark");
  }
});

function toggleTheme() {
  const root = document.documentElement;
  root.classList.toggle("dark");

  localStorage.setItem(
    "theme",
    root.classList.contains("dark") ? "dark" : "light"
  );
}
