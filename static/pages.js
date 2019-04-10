function showOrHideInfo(button, element, text) {
    description = document.getElementById(element);
    if (description.style.display === "none") {
        description.style.display = "block";
        button.innerHTML = "Hide " + text;
    } else {
        description.style.display = "none";
        button.innerHTML = "Display " + text;    }
}