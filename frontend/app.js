const API_BASE = "http://localhost:8006";
const API = `${API_BASE}/ToDoApp`;
const TOKEN_KEY = "todo_access_token";

let editingId = null;

const authForm = document.getElementById("auth-form");
const authSection = document.getElementById("auth-section");
const tasksSection = document.getElementById("tasks-section");
const authMessage = document.getElementById("auth-message");
const form = document.getElementById("task-form");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");

let isRegistering = false;
let accessToken = sessionStorage.getItem(TOKEN_KEY);

function parseTime(iso){
    return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso)?iso:iso+"Z");
}

function toLocalInput(iso) {
    const d = parseTime(iso);
    const pad = (n) => String(n).padStart(2,"0");
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function setAuthMessage(message) {
    authMessage.textContent = message;
}

function showTasks() {
    authSection.hidden = true;
    tasksSection.hidden = false;
    loadTasks();
    loadStats();
}

async function apiFetch(url, options = {}) {
    const headers = {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
    };
    return fetch(url, {...options, headers});
}

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username-input").value.trim();
    const password = document.getElementById("password-input").value;

    const endpoint = isRegistering
    ?  `${API_BASE}/Auth/register`
    :  `${API_BASE}/Auth/login`;

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password}),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Request failed");
        }

        if (isRegistering) {
            isRegistering = false;
            document.getElementById("auth-title").textContent = "Sign in";
            document.getElementById("toggle-auth").textContent = "Create account instead";
            setAuthMessage("Account Created. Please sign in.");
            return;
        }
        accessToken = result.access_token;
        sessionStorage.setItem(TOKEN_KEY, accessToken);
        setAuthMessage("");
        showTasks();
    } catch (error) {
        setAuthMessage(error.message);
    }
});

document.getElementById("toggle-auth").addEventListener("click", ()=>{
    isRegistering = !isRegistering;

    document.getElementById("auth-title").textContent = 
    isRegistering ? "Create account" : "sign in";

    document.getElementById("toggle-auth").textContent = isRegistering ? "back to sign in":"create account instead";

    setAuthMessage("");
})
function buildQuery() {
    const params = new URLSearchParams({limit:"100"});
    const status = document.getElementById("filter-status").value;
    const importance = document.getElementById("filter-importance").value;
    const search = document.getElementById("search-input").value.trim()
    if (status) {
        params.set("status",status);
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
    const res = await apiFetch(`${API}/tasks?${buildQuery()}`);
    if (!res.ok) {
        console.error("Failed to load tasks", res.status);
        return;
    }
    const tasks = await res.json();
    renderTasks(tasks);
}

async function loadStats() {
    const res = await apiFetch(`${API}/tasks/stats`);
    if (!res.ok) return;
    const s = await res.json();
    document.getElementById("stats").textContent = `Pending: ${s.pending} | Completed: ${s.completed} | Overdue: ${s.overdue}`;
}

function renderTasks(tasks) {
    const list = document.getElementById("task-list");
    list.innerHTML = "";

    if (tasks.length === 0) {
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
       imp.textContent = i.importance;

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
    const res = await apiFetch(`${API}/tasks/${id}/complete`, {method:"PATCH"});
    if (!res.ok) {
        console.error("Failed to complete task", res.status);
        return;
    }
    loadTasks();
}

async function deleteTask(id) {
    if (!confirm("Delete this task?")) return;
    const res = await apiFetch(`${API}/tasks/${id}`, {method: "DELETE"});
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
    const res = await apiFetch(url, {
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
    clearTimeout(searchTime);
    searchTime = setTimeout(loadTasks, 300);
});

if (accessToken) {
    showTasks();
} else {
    authSection.hidden = false;
    tasksSection.hidden = true;
}