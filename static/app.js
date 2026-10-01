(() => {
  const api = window.todoApi;
  const state = { todos: [], filter: "all", editingId: null };

  const el = {
    form: document.getElementById("add-form"),
    input: document.getElementById("new-title"),
    list: document.getElementById("todo-list"),
    empty: document.getElementById("empty"),
    tally: document.getElementById("tally"),
    error: document.getElementById("error"),
    clear: document.getElementById("clear-completed"),
    note: document.getElementById("mode-note"),
    filters: document.querySelectorAll("[data-filter]"),
  };

  const EMPTY_MESSAGES = {
    all: "Nothing on the list. Add your first to-do above.",
    active: "Nothing open. Everything is done.",
    completed: "Nothing done yet. Tick a box to mark a to-do done.",
  };

  function showError(message) {
    el.error.textContent = message;
    el.error.hidden = !message;
  }

  // Runs an API call, refreshes the list, and surfaces any error.
  async function run(action) {
    try {
      await action();
      state.todos = await api.list();
      showError("");
    } catch (err) {
      showError(err.message || "Something went wrong. Try again.");
    }
    render();
  }

  function visibleTodos() {
    if (state.filter === "active") return state.todos.filter((t) => !t.completed);
    if (state.filter === "completed") return state.todos.filter((t) => t.completed);
    return state.todos;
  }

  function render() {
    const open = state.todos.filter((t) => !t.completed).length;
    const done = state.todos.length - open;
    el.tally.textContent = `${open} open · ${done} done`;
    el.clear.hidden = done === 0;

    el.filters.forEach((btn) => {
      btn.setAttribute("aria-pressed", String(btn.dataset.filter === state.filter));
    });

    const todos = visibleTodos();
    el.list.replaceChildren(...todos.map(renderTodo));
    el.empty.hidden = todos.length > 0;
    el.empty.textContent = EMPTY_MESSAGES[state.filter];

    const editor = el.list.querySelector(".todo-edit");
    if (editor) {
      editor.focus();
      editor.select();
    }
  }

  function renderTodo(todo) {
    const li = document.createElement("li");
    li.className = "todo" + (todo.completed ? " is-done" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `todo-${todo.id}`;
    checkbox.checked = todo.completed;
    checkbox.setAttribute("aria-label", todo.title);
    checkbox.addEventListener("change", () =>
      run(() => api.update(todo.id, { completed: checkbox.checked })),
    );
    li.append(checkbox);

    if (state.editingId === todo.id) {
      li.append(renderEditor(todo));
      return li;
    }

    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;
    title.addEventListener("dblclick", () => startEditing(todo.id));

    const actions = document.createElement("div");
    actions.className = "todo-actions";
    actions.append(
      iconButton("Edit", `Edit "${todo.title}"`, "", () => startEditing(todo.id)),
      iconButton("Delete", `Delete "${todo.title}"`, "delete", () =>
        run(() => api.remove(todo.id)),
      ),
    );

    li.append(title, actions);
    return li;
  }

  function renderEditor(todo) {
    const input = document.createElement("input");
    input.className = "todo-edit";
    input.id = `edit-${todo.id}`;
    input.value = todo.title;
    input.maxLength = 200;
    input.setAttribute("aria-label", "Edit to-do");

    let finished = false;
    const finish = (save) => {
      if (finished) return;
      finished = true;
      state.editingId = null;
      const title = input.value.trim();
      if (save && title && title !== todo.title) {
        run(() => api.update(todo.id, { title }));
      } else {
        render();
      }
    };
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") finish(true);
      if (e.key === "Escape") finish(false);
    });
    input.addEventListener("blur", () => finish(true));
    return input;
  }

  function iconButton(label, ariaLabel, extraClass, onClick) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `icon-button ${extraClass}`.trim();
    btn.textContent = label;
    btn.setAttribute("aria-label", ariaLabel);
    btn.addEventListener("click", onClick);
    return btn;
  }

  function startEditing(id) {
    state.editingId = id;
    render();
  }

  el.form.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = el.input.value.trim();
    if (!title) {
      showError("Type something before adding a to-do.");
      return;
    }
    el.input.value = "";
    run(() => api.create(title));
  });

  el.filters.forEach((btn) => {
    btn.addEventListener("click", () => {
      state.filter = btn.dataset.filter;
      render();
    });
  });

  el.clear.addEventListener("click", () => run(() => api.clearCompleted()));

  if (api.note) {
    el.note.textContent = api.note;
    el.note.hidden = false;
  }

  run(async () => {});
})();
