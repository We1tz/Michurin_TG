let passwordInput = document.querySelector(".password");
let passwordBtn = document.querySelector(".pass-btn");

let passwordToggle = false;

passwordBtn.addEventListener("click", () => {
  passwordToggle = !passwordToggle;

  if (passwordToggle === true) {
    passwordInput.setAttribute("type", "text");
    passwordBtn.setAttribute("src", "./img/pass2.svg");
  } else if(passwordToggle === false) {
    passwordInput.setAttribute("type", "password");
    passwordBtn.setAttribute("src", "./img/pass1.svg");
  }
});

// if(passwordInput.classList.contains == 'password') {
//     passwordInput.setAttribute('type', 'password')
// } else {
//     passwordInput.setAttribute('type', 'text')
// }
