const API = "http://localhost:8006/ToDoApp";

async function loadTasks() {
    const res = await fetch(`${API}/tasks`);
    if (!res.ok) {
        console.error("Failed to load tasks", res.status);
        return;
    }
    const tasks = await res.json();
    renderTasks(tasks);
}

function renderTasks(tasks) {
    const list = document.getElementById("task-list");
    list.innerHTML = "";
    for (const i of tasks) {
       const li = document.createElement("li");
       li.textContent = `${i.task} | ${i.importance} | ${i.status} | ${new Date(i.time).toLocaleString()}`;
       list.appendChild(li);
    }
}

loadTasks();

const form = document.getElementById("task-form");

form.addEventListener("submit", async (event)=>{
    event.preventDefault();

    const body = {
        task: document.getElementById("task-input").value,
        time: new Date(document.getElementById("time-input").value).toISOString(),
        importance: document.getElementById("importance-input").value
    };

    const res = await fetch(`${API}/tasks`, {
    method: "POST",
    headers: {"Content-type": "application/json"},
    body: JSON.stringify(body),
    });

    if (!res.ok) {
        const err = await res.json();
        console.error("Failed to add task", res.status, err);
        alert("Could not add the task. Check the console for details.");
        return;
    }
    form.reset();
    loadTasks();
});

