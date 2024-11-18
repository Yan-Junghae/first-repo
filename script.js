// script.js
function changeText() {
  const welcomeText = document.getElementById("welcome-text");
  const button = document.getElementById("change-text-btn");
  
  // Change text content
  welcomeText.innerText = "JavaScript is Dynamic and Fun!";
  
  // Add a pulsating animation
  welcomeText.classList.add("pulse-animation");
  
  // Change button color randomly
  button.style.backgroundColor = getRandomColor();
}

// Function to generate a random color
function getRandomColor() {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}