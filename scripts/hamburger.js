document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.querySelector(".hamburger-menu");
  const navMenu = document.querySelector(".nav-menu");

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", function () {
      navMenu.classList.toggle("active");
      hamburger.classList.toggle("active");

      // Accessibility - update aria-expanded attribute
      const expanded = navMenu.classList.contains("active");
      hamburger.setAttribute("aria-expanded", expanded);
    });
  }
});
