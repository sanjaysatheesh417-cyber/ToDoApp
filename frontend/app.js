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
       const text = document.createElement("span");
       text.textContent = `${i.task} | ${i.importance} | ${i.status} | ${new Date(i.time).toLocaleString()}`;
       li.appendChild(text);

       if (i.status === "pending"){
        const doneBtn = document.createElement("button");
        doneBtn.textContent = "Complete";
        doneBtn.addEventListener("click", ()=>completeTask(i.id));
        li.appendChild(doneBtn)
       }

       const delBtn = document.createElement("button");
       delBtn.textContent = "Delete";
       delBtn.addEventListener("click", ()=>deleteTask(i.id));
       li.appendChild(delBtn);

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

async function completeTask(id) {
    const res = await fetch(`${API}/tasks/${id}/complete`, {method:"PATCH"});
    if (!res.ok) {
        console.error("Failed to complete task", res.status);
        return;
    }
    loadTasks();
}

async function deleteTask(id) {
    if (!confirm("Delete this task?")) return;
    const res = await fetch(`${API}/tasks/${id}`, {method: "DELETE"});
    if (res.status !== 204) {
        console.error("Failed to delete task", res.status);
        return;
    }
    loadTasks();
}