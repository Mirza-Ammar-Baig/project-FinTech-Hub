// JavaScript code to trigger animation when the page loads
document.addEventListener("DOMContentLoaded", function() {
    const mainElement = document.querySelector("main");
    mainElement.style.opacity = 0; // Ensure it starts hidden
    setTimeout(function() {
        mainElement.style.animation = "fadeIn 1s ease forwards";
        mainElement.style.opacity = 1;
    }, 500); // Delay the animation start by 500 milliseconds
});
