function showOrHideInfo(button) {
    description = document.getElementById("description");
    if (description.style.display === "none") {
        description.style.display = "block";
        button.innerHTML = "Hide introduction"
    } else {
        description.style.display = "none";
        button.innerHTML = "Display introduction"
    }
}