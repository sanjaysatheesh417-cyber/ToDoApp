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