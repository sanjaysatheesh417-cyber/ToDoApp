const API = "http://localhost:8006/ToDoApp";
let editingId = null;

const form = document.getElementById("task-form");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");

function parseTime(iso){
    return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso)?iso:iso+"Z");
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
    };
    if (importance){
        params.set("importance",importance)
    };
    if (search) {
        params.set("search",search);
    };
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
    document.getElementById("stats").textContent = `Pending: ${s.pending} | Completed: ${s.completed} | Overdue: ${s.overdue}`;
}

function renderTasks(tasks) {
    const list = document.getElementById("task-list");
    list.innerHTML = "";

    if (tasks.lenght === 0) {
        const empty = document.createElement("li");
        empty.className="empty";
        empty.textContent = "No tasks found.";
        list.appendChild(empty);
        return;
    }

    for (const i of tasks) {
       const li = document.createElement("li");

       const isOverdue = i.status === "pending" && parseTime(i.time) < new Date();
       if (isOverdue) {
        li.classList.add("overdue");
       };
       if (i.status === "completed") {
        li.classList.add("done");
       };

       const main = document.createElement("div");
       main.className = "task-main";
       const title = document.createElement("span");
       title.className = "task-title";
       title.textContent = i.task;

       const meta = document.createElement("div");
       meta.className = "task-meta";
       const imp = document.createElement("span");
       meta.className = `badge badge-${i.importance}`;

       const due = document.createElement("span");
       due.className = "due";
       due.textContent = `Due ${parseTime(i.time).toLocaleString()}`;

       meta.append(imp, due);
       main.append(title, meta);
       li.appendChild(main);
       
       const actions = document.createElement("span");
       actions.className = "actions";

       if (i.status === "pending"){
        const doneBtn = document.createElement("button");
        doneBtn.textContent = "Complete";
        doneBtn.addEventListener("click", ()=>completeTask(i.id));
        actions.appendChild(doneBtn)
       }

       const editBtn = document.createElement("button");
       editBtn.textContent = "Edit";
       editBtn.addEventListener("click", ()=>startEdit(i));
       actions.appendChild(editBtn);
       
       const delBtn = document.createElement("button");
       delBtn.textContent = "Delete";
       delBtn.addEventListener("click", ()=>deleteTask(i.id));
       actions.appendChild(delBtn);

       li.appendChild(actions);
       list.appendChild(li);
    }
};

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

function startEdit(t) {
    editingId = t.id;
    document.getElementById("task-input").value = t.task;
    document.getElementById("time-input").value = toLocalInput(t.time);
    document.getElementById("importance-input").value = t.importance;
    submitBtn.textContent = "save changes";
    cancelBtn.hidden = true;
    document.getElementById("task-input").focus()
}

function resetFrom() {
    form.reset()
    editingId = null;
    submitBtn.textContent = "Add Task";
    cancelBtn.hidden = true;
}

cancelBtn.addEventListener("click", resetFrom);

form.addEventListener("submit", async (event)=>{
    event.preventDefault();

    const body = {
        task: document.getElementById("task-input").value,
        time: new Date(document.getElementById("time-input").value).toISOString(),
        importance: document.getElementById("importance-input").value
    };

    const isEdit = editingId !== null;
    const url = isEdit ? `${API}/tasks/${editingId}` : `${API}/tasks`;
    const res = await fetch(url, {
    method: isEdit ? "PATCH": "POST",
    headers: {"Content-type": "application/json"},
    body: JSON.stringify(body),
    });

    if (!res.ok) {
        const err = await res.json();
        console.error("Failed to add task", res.status, err);
        alert("Could not add the task. Check the console for details.");
        return;
    }
    resetFrom();
    loadTasks();
});

document.getElementById("filter-status").addEventListener("change", loadTasks);
document.getElementById("filter-importance").addEventListener("change", loadTasks);

let searchTime;
document.getElementById("search-input").addEventListener("input", ()=>{
    clearTimeOut(searchTimer);
    searchTime = setTimeout(loadTasks, 300);
});

loadTasks();