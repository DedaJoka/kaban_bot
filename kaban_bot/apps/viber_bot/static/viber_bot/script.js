document.addEventListener("DOMContentLoaded", function () {
  const listOfWorksButton = document.getElementById("listOfWorksButton");
  const listOfWorksList = document.getElementById("listOfWorksList");

  listOfWorksButton.addEventListener("click", function () {
    listOfWorksList.classList.toggle("hidden");
  });


  const listOfCertificatesButton = document.getElementById("listOfCertificatesButton");
  const listOfCertificatesList = document.getElementById("listOfCertificatesList");

  listOfCertificatesButton.addEventListener("click", function () {
    console.log("click button")
    listOfCertificatesList.classList.toggle("hidden");
  });
});
