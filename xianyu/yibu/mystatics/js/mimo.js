
const item = document.querySelector("div");

function changeShape() {
    item.classList.toggle("purple");
}

item.addEventListener("click", changeShape);

