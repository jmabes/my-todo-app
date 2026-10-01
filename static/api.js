// HTTP client for the FastAPI backend. app.js only talks to window.todoApi,
// so an alternative implementation (see preview/local-api.js) can be swapped in.
window.todoApi = (() => {
  async function request(path, options = {}) {
    const res = await fetch(`api/todos${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(await errorMessage(res));
    return res.status === 204 ? null : res.json();
  }

  async function errorMessage(res) {
    try {
      const { detail } = await res.json();
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    } catch {
      // Fall through to the generic message.
    }
    return `Request failed (${res.status})`;
  }

  return {
    note: null,
    list: () => request(""),
    create: (title) => request("", { method: "POST", body: JSON.stringify({ title }) }),
    update: (id, changes) =>
      request(`/${id}`, { method: "PATCH", body: JSON.stringify(changes) }),
    remove: (id) => request(`/${id}`, { method: "DELETE" }),
    clearCompleted: () => request("/completed", { method: "DELETE" }),
  };
})();
