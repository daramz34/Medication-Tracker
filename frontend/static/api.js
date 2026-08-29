/* Small, shared client for the D-Med Tracker API. */
const DMedAPI = (() => {
  const base = "/api/v1";
  const tokenKey = "dmed_access_token";

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const token = localStorage.getItem(tokenKey);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(`${base}${path}`, { ...options, headers });
    if (response.status === 401) localStorage.removeItem(tokenKey);
    if (response.status === 204) return null;
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();
    if (!response.ok) {
      const detail = payload && typeof payload === "object" ? payload.detail : payload;
      throw new Error(detail || `Request failed (${response.status})`);
    }
    return payload;
  }

  return {
    tokenKey,
    isAuthenticated: () => Boolean(localStorage.getItem(tokenKey)),
    logout: () => localStorage.removeItem(tokenKey),
    register: (data) => request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
    login: async (username, password) => {
      const body = new URLSearchParams({ username, password });
      const result = await request("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      localStorage.setItem(tokenKey, result.access_token);
      localStorage.setItem("dmed_username", username);
      return result;
    },
    medications: () => request("/medications/").then((items) => items || []),
    medication: (id) => request(`/medications/${id}`),
    createMedication: (data) => request("/medications/", { method: "POST", body: JSON.stringify(data) }),
    updateMedication: (id, data) => request(`/medications/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    updateStatus: (id, status) => request(`/medications/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
    deleteMedication: (id) => request(`/medications/${id}`, { method: "DELETE" }),
    todayLogs: () => request("/logs/today").then((items) => items || []),
    logs: (id) => request(`/logs/${id}`).then((items) => items || []),
    log: (data) => request("/logs/", { method: "POST", body: JSON.stringify(data) }),
    streak: (id) => request(`/streaks/${id}`),
  };
})();
