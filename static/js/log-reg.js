// !Add focus on input fields
const allInputs = document.querySelectorAll(".input input");

function updateWrapperFocusState(input) {
  const wrapper = input.parentElement;
  if (input.value.trim().length > 0) {
    wrapper.classList.add("focused");
  } else {
    wrapper.classList.remove("focused");
  }
}

// !Set event listeners for all inputs
allInputs.forEach((input) => {
  input.addEventListener("focus", () => updateWrapperFocusState(input));
  input.addEventListener("blur", () => updateWrapperFocusState(input));
  input.addEventListener("input", () => updateWrapperFocusState(input));

  // !Initial state check (in case of autofill)
  updateWrapperFocusState(input);
});



// !show Password
const passwordInput = document.getElementById("password");
const eye = document.getElementById("eye");
const close_eye = document.getElementById("close_eye");

// !Hide both icons initially
eye.style.display = "none";
close_eye.style.display = "none";

// !Toggle password visibility
function showPassword() {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    close_eye.style.display = "block";
    eye.style.display = "none";
  } else {
    passwordInput.type = "password";
    close_eye.style.display = "none";
    eye.style.display = "block";
  }
}
// !Show eye icon when user starts typing
passwordInput.addEventListener("input", () => {
  if (passwordInput.value.length > 0) {
    if (passwordInput.type === "password") {
      eye.style.display = "block";
    } else {
      close_eye.style.display = "block";
    }
  } else {
    eye.style.display = "none";
    close_eye.style.display = "none";
  }
});
