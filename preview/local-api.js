// Browser-only stand-in for static/api.js, used by the shareable preview build.
// Mirrors the backend's validation and responses, but keeps data in
// localStorage (falling back to memory when storage is unavailable).
window.todoApi = (() => {
  const KEY = "todo-preview-v1";
  const MAX_TITLE = 200;
  const EXAMPLES = [
    { title: "Book dentist appointment", completed: false },
    { title: "Water the plants", completed: true },
    { title: "Draft the quarterly budget", completed: false },
  ];

  let memory = null;

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) return JSON.parse(raw);
    } catch {
      // Storage blocked or corrupt: fall back to memory below.
    }
    if (memory) return memory;
    const now = new Date().toISOString();
    return {
      nextId: EXAMPLES.length + 1,
      todos: EXAMPLES.map((t, i) => ({ id: i + 1, created_at: now, ...t })),
    };
  }

  function save(db) {
    memory = db;
    try {
      localStorage.setItem(KEY, JSON.stringify(db));
    } catch {
      // Keep the in-memory copy only.
    }
  }

  function validTitle(title) {
    const trimmed = String(title ?? "").trim();
    if (!trimmed) throw new Error("Title can't be empty.");
    if (trimmed.length > MAX_TITLE) throw new Error(`Keep titles under ${MAX_TITLE} characters.`);
    return trimmed;
  }

  function find(db, id) {
    const todo = db.todos.find((t) => t.id === id);
    if (!todo) throw new Error("To-do not found");
    return todo;
  }

  const clone = (value) => JSON.parse(JSON.stringify(value));

  return {
    note: "Preview: the Python server isn't running here, so to-dos are saved in this browser only. The first three are examples.",
    async list() {
      return clone(load().todos);
    },
    async create(title) {
      const db = load();
      const todo = {
        id: db.nextId++,
        title: validTitle(title),
        completed: false,
        created_at: new Date().toISOString(),
      };
      db.todos.push(todo);
      save(db);
      return clone(todo);
    },
    async update(id, changes) {
      const db = load();
      const todo = find(db, id);
      if (changes.title !== undefined) todo.title = validTitle(changes.title);
      if (changes.completed !== undefined) todo.completed = Boolean(changes.completed);
      save(db);
      return clone(todo);
    },
    async remove(id) {
      const db = load();
      find(db, id);
      db.todos = db.todos.filter((t) => t.id !== id);
      save(db);
      return null;
    },
    async clearCompleted() {
      const db = load();
      const before = db.todos.length;
      db.todos = db.todos.filter((t) => !t.completed);
      save(db);
      return { deleted: before - db.todos.length };
    },
  };
})();
