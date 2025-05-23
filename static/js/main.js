// !light and dark mode
const body = document.getElementById("body");

const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") {
  body.classList.add("dark-mode");
} else {
  body.classList.remove("dark-mode");
}

function darkLight() {
  body.classList.toggle("dark-mode");

  if (body.classList.contains("dark-mode")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
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
const button = document.querySelector(".task-submit");

// !Check input value on page load
if (input.value.trim().length > 0) {
  button.style.display = "inline-block";
} else {
  button.style.display = "none";
}

// !Listen for input changes
input.addEventListener("input", () => {
  if (input.value.trim().length > 0) {
    button.style.display = "inline-block";
  } else {
    button.style.display = "none";
  }
});

document.querySelectorAll(".flex-te").forEach((taskBlock) => {
  // Details
  const openBtn = taskBlock.querySelector(".open-details");
  const modal = taskBlock.querySelector(".details-modal");
  const closeBtn = modal?.querySelector(".close");

  if (openBtn && modal && closeBtn) {
    openBtn.addEventListener("click", (e) => {
      e.preventDefault();
      modal.style.display = "block";
    });

    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  // Delete
  const deleteBtn = taskBlock.querySelector(".delete-task");
  const delModal = taskBlock.querySelector(".delete-modal");
  const closeDel = delModal?.querySelector(".close");
  const backBtn = delModal?.querySelector(".db-back");

  if (deleteBtn && delModal && closeDel && backBtn) {
    deleteBtn.addEventListener("click", (e) => {
      e.preventDefault();
      delModal.style.display = "block";
    });

    closeDel.addEventListener("click", () => {
      delModal.style.display = "none";
    });

    backBtn.addEventListener("click", () => {
      delModal.style.display = "none";
    });
  }

  // Edit
  const editBtn = taskBlock.querySelector(".edit-task");
  const editModal = taskBlock.querySelector(".edit-modal");
  const closeEdit = editModal?.querySelector(".close");
  const taskInput = editModal?.querySelector("input[name='add_task']");
  const dueDateInput = editModal?.querySelector("input[name='due_date']");

  if (editBtn && editModal && closeEdit) {
    editBtn.addEventListener("click", (e) => {
      e.preventDefault();
      const taskText = editBtn.getAttribute("data-task-text");
      const dueDate = editBtn.getAttribute("data-due-date");

      if (taskInput) taskInput.value = taskText;
      if (dueDateInput) dueDateInput.value = dueDate;

      editModal.style.display = "block";
    });

    closeEdit.addEventListener("click", () => {
      editModal.style.display = "none";
    });
  }
});

