document.addEventListener("DOMContentLoaded", function () {
  let isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

  const signedOutNav = document.getElementById("signed-out-nav");
  const signedInNav = document.getElementById("signed-in-nav");
  const logoutBtn = document.getElementById("logout-btn");

  if (isLoggedIn) {
    signedInNav.style.display = "flex";
    signedOutNav.style.display = "none";
  } else {
    signedInNav.style.display = "none";
    signedOutNav.style.display = "flex";
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      localStorage.setItem("isLoggedIn", "false");
      location.reload();
    });
  }
});
