document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".upload-form");
    const loadingModal = document.getElementById("loadingModal");
    const successModal = document.getElementById("successModal");

    form.addEventListener("submit", (event) => {
        const files = document.querySelector(".file-input").files;
        if (files.length === 0) {
            event.preventDefault();
            alert("Lūdzu, izvēlieties failus augšupielādei!");
        } else {
            loadingModal.style.display = "flex";
        }
    });

    if (loadingModal) {
        setTimeout(() => {
            loadingModal.style.display = "none";
        }, 1500); 
    }
});
