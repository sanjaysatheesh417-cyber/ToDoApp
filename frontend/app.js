const API = "http://localhost:8006/ToDoApp";
let editingId = null;

const form = document.getElementById("task-form");
const subitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");

function parseTime(iso){
    return new Date(/[Zz]|[+-]\d\d:\d\d$/.test(iso)?iso:iso+"Z");
}

function toLocalInput(iso) {
    const d = parseTime(iso);
    const pad = (n) => String(n).padStart(2,"0");
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function buildQuery() {
    const params = new URLSearchParams({limit:"100"});
    const status = document.getElementById("filter-status").value;
    const importance = document.getElementById("filter-importance").value;
    const search = document.getElementById("search-input").value.trim()
    if (status) {
        params.set("status".status);
    }
    if (importance){
        params.set("importance",importance)
    }
    if (search) {
        params.set("search",search);
    }
    return params.toString()
}

async function loadTasks() {
    const res = await fetch(`${API}/tasks`);
    if (!res.ok) {
        console.error("Failed to load tasks", res.status);
        return;
    }
    const tasks = await res.json();
    renderTasks(tasks);
    loadStats();
}

async function loadStats() {
    const res = await fetch(`${API}/tasks/stats`);
    if (!res.ok) return;
    const s = await res.json();
    document.getElementById("stats").textContent = `Pending: ${s.pending} | Completed: ${s.completed} | Overdue: $(s.overdue)`;
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