/* Get the modal and image elements */
let modal = document.getElementById("imageModal");
let modalImg = document.getElementById("modalImage");

/* Get all images with the class "rounded-image" */
let images = document.querySelectorAll(".rounded-image");

/* Get the close button */
let closeModal = document.getElementById("closeModal");

/* Loop through all images and add an event listener to each */
images.forEach(function (image) {
  image.addEventListener("click", function () {
      modal.style.display = "block";
      modalImg.src = this.src;
  });
});

/* Close the modal when the close button is clicked */
closeModal.onclick = function () {
  modal.style.display = "none";
};

/* Close the modal when the user clicks outside the modal */
window.onclick = function (event) {
  if (event.target === modal) {
      modal.style.display = "none";
  }
};
