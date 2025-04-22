// DOM Elements
export const modal = document.getElementById("modal");
const modalBackdrop = document.getElementById("modalBackdrop");
const closeModalBtn = document.getElementById("closeModal");

// Open modal function
export function openModal() {
    modal.classList.remove("hidden");
    modalBackdrop.classList.remove("hidden");
    document.body.style.overflow = "hidden"; // Prevent scrolling
}

// Close modal function
export function closeModal() {
    modal.classList.add("hidden");
    modalBackdrop.classList.add("hidden");
    document.body.style.overflow = "auto"; // Enable scrolling
}

// Event listeners
closeModalBtn.addEventListener("click", closeModal);

// Close modal when clicking on backdrop
modalBackdrop.addEventListener("click", closeModal);

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
        closeModal();
    }
});
