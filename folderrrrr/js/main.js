// !light and dark mode
const body = document.getElementById("body");

function darkLight() {
  body.classList.toggle("dark-mode");
}

// !toggle nav bar
const toggle_bar = document.getElementById("toggle");
const nav = document.getElementById("nav");
const sideDark = document.getElementById("sideDark");

function openNav() {
  nav.classList.toggle("nav-active");
  toggle_bar.classList.toggle("toggle-active");
  sideDark.classList.toggle("activeDark");
}

function closeNav() {
  nav.classList.toggle("nav-active");
  toggle_bar.classList.toggle("toggle-active");
  sideDark.classList.remove("activeDark");
}

// !Edit items
const edit_button = document.querySelectorAll(".edit-i");
const items = document.querySelectorAll(".items");

// !Toggle menu when edit icon is clicked
edit_button.forEach((icon) => {
  icon.addEventListener("click", (e) => {
    e.stopPropagation();
    const parent = icon.closest(".edit-items");
    const itemsMenu = parent.querySelector(".items");

    items.forEach((menu) => {
      if (menu !== itemsMenu) {
        menu.classList.remove("active");
      }
    });

    itemsMenu.classList.toggle("active");
  });
});

// !Hide all menus when clicking outside
document.addEventListener("click", (e) => {
  items.forEach((menu) => {
    menu.classList.remove("active");
  });
});

// !Add task, shows task button when input length > 0
const input = document.querySelector("input[name='add_task']");
const button = document.querySelector("button[type='submit']");

// !Hide button initially
button.style.display = "none";

// !Listen for input changes
input.addEventListener("input", () => {
  if (input.value.trim().length > 0) {
    button.style.display = "inline-block";
  } else {
    button.style.display = "none";
  }
});

document.querySelectorAll(".flex-te").forEach((taskBlock) => {
  const openBtn = taskBlock.querySelector(".open-details");
  const modal = taskBlock.querySelector(".details-modal");
  const closeBtn = modal.querySelector(".details-modal .close");

  openBtn.addEventListener("click", (e) => {
    e.preventDefault();
    modal.style.display = "block";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
});
