// ================= CSRF TOKEN =================
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}

// ================= LIKE BUTTON =================
function likeRecipe(id, btn) {
    fetch(`/like/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        }
    })
    .then(res => res.json())
    .then(data => {
        btn.querySelector("span").innerText = data.count;

        // animation
        btn.style.transform = "scale(1.2)";
        setTimeout(() => {
            btn.style.transform = "scale(1)";
        }, 200);
    });
}


// ================= RATING =================
function rateRecipe(recipeId, value, starsContainer) {
    fetch(`/rate/${recipeId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ rating: value })
    })
    .then(res => res.json())
    .then(data => {
        alert("⭐ Rating submitted!");
    });
}


// ================= COMMENTS =================
function addComment(recipeId) {
    let input = document.getElementById(`comment-input-${recipeId}`);
    let text = input.value;

    if (!text.trim()) return;

    fetch(`/comment/${recipeId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {
        let list = document.getElementById(`comment-list-${recipeId}`);

        let newComment = document.createElement("p");
        newComment.innerHTML = `<b>${data.user}:</b> ${data.text}`;

        list.prepend(newComment);
        input.value = "";
    });
}


// ================= AI SUGGESTION =================
function getAISuggestion() {
    fetch("/ai/")
    .then(res => res.json())
    .then(data => {
        document.getElementById("ai-box").innerText = data.suggestion;
    });
}


// ================= MEAL PLANNER =================

// drag
function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

// allow drop
function allowDrop(ev) {
    ev.preventDefault();
}

// drop + SAVE
function drop(ev, day) {
    ev.preventDefault();

    let data = ev.dataTransfer.getData("text");
    let node = document.getElementById(data).cloneNode(true);

    node.setAttribute("draggable", "false");

    ev.target.innerHTML = "";
    ev.target.appendChild(node);

    let recipeId = data.split("-")[1];

    // SAVE to DB
    fetch("/save-meal/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            recipe_id: recipeId,
            day: day
        })
    });
}


// ================= LOAD SAVED MEALS =================
function loadMeals() {
    fetch("/get-meals/")
    .then(res => res.json())
    .then(data => {
        data.forEach(meal => {
            let box = document.getElementById(`day-${meal.day}`);
            if (box) {
                box.innerHTML = `<div class="recipe">${meal.recipe}</div>`;
            }
        });
    });
}


// ================= RUN ON LOAD =================
document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("ai-box")) {
        getAISuggestion();
    }

    if (document.getElementById("planner")) {
        loadMeals();
    }
});