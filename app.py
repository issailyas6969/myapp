from flask import Flask, request, jsonify, render_template_string
import json, os

app = Flask(__name__)
DATA_FILE = "todos.json"

def load_todos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Todo App — Deployed on EC2</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 40px 16px; }
    .card { background: white; border-radius: 12px; padding: 32px; width: 100%; max-width: 520px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
    h1 { font-size: 22px; margin-bottom: 4px; }
    .sub { font-size: 13px; color: #888; margin-bottom: 24px; }
    .add-row { display: flex; gap: 8px; margin-bottom: 24px; }
    input[type=text] { flex: 1; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; outline: none; }
    input[type=text]:focus { border-color: #4f46e5; }
    button.add-btn { background: #4f46e5; color: white; border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-size: 15px; }
    button.add-btn:hover { background: #4338ca; }
    .todo-list { list-style: none; }
    .todo-item { display: flex; align-items: center; gap: 10px; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
    .todo-item:last-child { border-bottom: none; }
    .todo-text { flex: 1; font-size: 15px; }
    .todo-text.done { text-decoration: line-through; color: #aaa; }
    .btn-done { background: #d1fae5; color: #065f46; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
    .btn-done:hover { background: #a7f3d0; }
    .btn-del { background: #fee2e2; color: #991b1b; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
    .btn-del:hover { background: #fca5a5; }
    .empty { text-align: center; color: #bbb; padding: 32px 0; font-size: 14px; }
    .badge { font-size: 12px; background: #eef2ff; color: #4f46e5; padding: 2px 8px; border-radius: 20px; margin-left: 8px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>📝 Todo App <span class="badge" id="count"></span></h1>
    <p class="sub">Auto-deployed to AWS EC2 via LangGraph</p>
    <div class="add-row">
      <input type="text" id="task-input" placeholder="Add a new task..." onkeydown="if(event.key==='Enter') addTodo()"/>
      <button class="add-btn" onclick="addTodo()">Add</button>
    </div>
    <ul class="todo-list" id="todo-list"></ul>
  </div>

  <script>
    async function fetchTodos() {
      const res = await fetch('/api/todos');
      const todos = await res.json();
      const list = document.getElementById('todo-list');
      const count = document.getElementById('count');
      count.textContent = todos.filter(t => !t.done).length + ' pending';
      if (todos.length === 0) {
        list.innerHTML = '<div class="empty">No tasks yet. Add one above!</div>';
        return;
      }
      list.innerHTML = todos.map(t => `
        <li class="todo-item">
          <span class="todo-text ${t.done ? 'done' : ''}">${t.text}</span>
          ${!t.done ? `<button class="btn-done" onclick="completeTodo(${t.id})">✓ Done</button>` : ''}
          <button class="btn-del" onclick="deleteTodo(${t.id})">✕ Delete</button>
        </li>
      `).join('');
    }

    async function addTodo() {
      const input = document.getElementById('task-input');
      const text = input.value.trim();
      if (!text) return;
      await fetch('/api/todos', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text}) });
      input.value = '';
      fetchTodos();
    }

    async function completeTodo(id) {
      await fetch(`/api/todos/${id}/complete`, { method: 'PUT' });
      fetchTodos();
    }

    async function deleteTodo(id) {
      await fetch(`/api/todos/${id}`, { method: 'DELETE' });
      fetchTodos();
    }

    fetchTodos();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/todos", methods=["GET"])
def get_todos():
    return jsonify(load_todos())

@app.route("/api/todos", methods=["POST"])
def add_todo():
    todos = load_todos()
    data = request.get_json()
    new_id = max([t["id"] for t in todos], default=0) + 1
    todos.append({"id": new_id, "text": data["text"], "done": False})
    save_todos(todos)
    return jsonify({"ok": True})

@app.route("/api/todos/<int:todo_id>/complete", methods=["PUT"])
def complete_todo(todo_id):
    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
    save_todos(todos)
    return jsonify({"ok": True})

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
