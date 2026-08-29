const DMed = (() => {
  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  }[char]));
  const title = (value) => String(value || "").replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  const date = (value) => {
    if (!value) return "—";
    return new Date(`${String(value).slice(0, 10)}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  };
  const time = (value) => value ? String(value).slice(0, 5) : "—";
  const initials = (name) => String(name || "D").slice(0, 2).toUpperCase();
  const toast = (message, error = false) => {
    const node = $("#toast");
    if (!node) return;
    node.textContent = message;
    node.className = `toast show${error ? " error" : ""}`;
    window.clearTimeout(node.toastTimer);
    node.toastTimer = window.setTimeout(() => { node.className = "toast"; }, 3200);
  };
  const requireAuth = () => {
    if (!DMedAPI.isAuthenticated()) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      return false;
    }
    return true;
  };
  const statusBadge = (status) => `<span class="status-badge status-${escape(status)}">${escape(title(status))}</span>`;
  const medIcon = (name) => `<span class="med-icon" aria-hidden="true">${escape(String(name || "M").slice(0, 1).toUpperCase())}</span>`;
  const setUserChrome = () => {
    const username = localStorage.getItem("dmed_username") || "Your account";
    $$(".js-username").forEach((node) => { node.textContent = username; });
    $$(".js-avatar").forEach((node) => { node.textContent = initials(username); });
    $$(".js-logout").forEach((node) => { node.onclick = () => {
      DMedAPI.logout();
      window.location.href = "/";
    }; });
    const current = window.location.pathname;
    $$(".side-nav a, .site-nav a").forEach((link) => {
      if (link.pathname === current || (current === "/app" && link.pathname === "/app")) link.classList.add("active");
    });
    const menu = $(".mobile-menu");
    if (menu) menu.onclick = () => $(".sidebar").classList.toggle("open");
  };

  function setupAuth() {
    const form = $("#auth-form");
    if (!form) return;
    const loginTab = $("#login-tab");
    const registerTab = $("#register-tab");
    const nameField = $("#name-field");
    const emailField = $("#email-field");
    const heading = $("#auth-heading");
    const intro = $("#auth-intro");
    const submit = $("#auth-submit");
    let mode = new URLSearchParams(window.location.search).get("mode") === "register" ? "register" : "login";
    const render = () => {
      const register = mode === "register";
      loginTab.classList.toggle("active", !register);
      registerTab.classList.toggle("active", register);
      emailField.classList.toggle("hidden", !register);
      $("#auth-email").required = register;
      $("#auth-username").placeholder = register ? "Choose a username" : "Your username";
      $("#username-label").textContent = "Username";
      heading.textContent = register ? "Create your account" : "Welcome back";
      intro.textContent = register ? "Start building a calmer medication routine." : "Sign in to see your medication plan.";
      submit.textContent = register ? "Create account" : "Sign in";
      $("#auth-password").autocomplete = register ? "new-password" : "current-password";
    };
    loginTab.addEventListener("click", () => { mode = "login"; render(); });
    registerTab.addEventListener("click", () => { mode = "register"; render(); });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const error = $("#auth-error");
      error.textContent = "";
      submit.disabled = true;
      try {
        const data = new FormData(form);
        if (mode === "register") {
          await DMedAPI.register({ username: data.get("username"), email: data.get("email"), password: data.get("password") });
          await DMedAPI.login(data.get("username"), data.get("password"));
        } else {
          await DMedAPI.login(data.get("username"), data.get("password"));
        }
        const next = new URLSearchParams(window.location.search).get("next") || "/app";
        window.location.href = next;
      } catch (err) {
        error.textContent = err.message;
      } finally {
        submit.disabled = false;
      }
    });
    render();
  }

  const medicationCard = (med, log) => {
    const logged = log && log.status;
    return `<article class="med-row">
      ${medIcon(med.name)}
      <div class="med-copy"><strong>${escape(med.name)}</strong><small>${escape(med.dosage)} · ${escape(title(med.frequency))} · ${time(med.reminder_time)}</small></div>
      ${logged ? statusBadge(logged) : `<button class="button button-soft button-small js-log" data-id="${med.id}">Mark taken</button>`}
      <div class="med-row-actions"><a class="icon-button" href="/medications/${med.id}" aria-label="View details">↗</a></div>
    </article>`;
  };

  async function setupDashboard() {
    if (!requireAuth()) return;
    setUserChrome();
    const list = $("#dashboard-medications");
    try {
      const [meds, logs] = await Promise.all([DMedAPI.medications(), DMedAPI.todayLogs()]);
      const byMed = Object.fromEntries(logs.map((log) => [log.medication_id, log]));
      const active = meds.filter((med) => med.status === "active");
      const taken = logs.filter((log) => log.status === "taken").length;
      $("#stat-active").textContent = active.length;
      $("#stat-taken").textContent = taken;
      $("#stat-total").textContent = meds.length;
      $("#medication-count").textContent = `${active.length} active`;
      list.innerHTML = meds.length ? meds.slice(0, 5).map((med) => medicationCard(med, byMed[med.id])).join("") :
        `<div class="empty-state"><div class="empty-mark">✚</div><p>No medications yet.</p><a class="text-link" href="/medications">Add your first medication</a></div>`;
      $$(".js-log", list).forEach((button) => button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await DMedAPI.log({ medication_id: Number(button.dataset.id), status: "taken" });
          toast("Medication marked as taken");
          setupDashboard();
        } catch (err) { toast(err.message, true); button.disabled = false; }
      }));
      const primary = active[0];
      if (primary) {
        try {
          const streak = await DMedAPI.streak(primary.id);
          $("#progress-value").textContent = `${Math.min(100, Math.round(streak.completion_percentage || 0))}%`;
          $("#progress-fill").style.width = `${Math.min(100, streak.completion_percentage || 0)}%`;
          $("#current-streak").textContent = `${streak.current_streak || 0} day${streak.current_streak === 1 ? "" : "s"}`;
          $("#longest-streak").textContent = `${streak.longest_streak || 0} days`;
        } catch (_) { /* an empty streak is still a valid dashboard state */ }
      }
    } catch (err) {
      list.innerHTML = `<div class="empty-state">${escape(err.message)}</div>`;
    }
  }

  function medicationFormData(form) {
    const data = new FormData(form);
    return {
      name: data.get("name"), description: data.get("description") || "No description",
      dosage: data.get("dosage"), frequency: data.get("frequency"),
      duration_days: Number(data.get("duration_days")), start_date: data.get("start_date"),
      reminder_time: data.get("reminder_time"), reminder_enabled: data.get("reminder_enabled") === "on",
    };
  }

  function openMedicationModal(med = null) {
    const backdrop = $("#med-modal");
    if (!backdrop) return;
    backdrop.classList.remove("hidden");
    $("#modal-title").textContent = med ? "Edit medication" : "Add medication";
    const form = $("#medication-form");
    form.reset();
    form.dataset.id = med ? med.id : "";
    if (med) {
      Object.entries({ name: med.name, description: med.description, dosage: med.dosage, frequency: med.frequency,
        duration_days: med.duration_days, start_date: med.start_date, reminder_time: time(med.reminder_time) }).forEach(([key, value]) => {
        if (form.elements[key]) form.elements[key].value = value;
      });
      form.elements.reminder_enabled.checked = med.reminder_enabled;
    } else {
      form.elements.start_date.value = new Date().toISOString().slice(0, 10);
      form.elements.reminder_enabled.checked = true;
    }
  }

  async function setupMedications() {
    if (!requireAuth()) return;
    setUserChrome();
    const list = $("#med-list");
    const render = async () => {
      const meds = await DMedAPI.medications();
      const query = ($("#med-search")?.value || "").toLowerCase();
      const visible = meds.filter((med) => med.name.toLowerCase().includes(query));
      list.innerHTML = visible.length ? visible.map((med) => `<article class="med-row">
        ${medIcon(med.name)}<div class="med-copy"><strong>${escape(med.name)}</strong><small>${escape(med.dosage)} · ${escape(title(med.frequency))} · ${date(med.start_date)} – ${date(med.end_date)}</small></div>
        ${statusBadge(med.status)}<div class="med-row-actions"><div class="log-actions" aria-label="Log today's dose"><button class="button button-soft button-small js-log-status" data-id="${med.id}" data-status="taken">Taken</button><button class="button button-ghost button-small js-log-status" data-id="${med.id}" data-status="missed">Missed</button><button class="button button-ghost button-small js-log-status" data-id="${med.id}" data-status="skipped">Skipped</button></div><select class="status-select js-update-status" data-id="${med.id}" aria-label="Change medication status"><option value="active" ${med.status === "active" ? "selected" : ""}>Active</option><option value="completed" ${med.status === "completed" ? "selected" : ""}>Completed</option><option value="abandoned" ${med.status === "abandoned" ? "selected" : ""}>Abandoned</option></select><button class="icon-button js-edit" data-id="${med.id}" aria-label="Edit">✎</button><button class="icon-button js-delete" data-id="${med.id}" aria-label="Delete">×</button><a class="icon-button" href="/medications/${med.id}" aria-label="View details">↗</a></div>
      </article>`).join("") : `<div class="empty-state"><div class="empty-mark">✚</div><p>${query ? "No medications match your search." : "Your medication list is empty."}</p></div>`;
      $$(".js-edit", list).forEach((button) => button.addEventListener("click", async () => openMedicationModal(meds.find((med) => med.id === Number(button.dataset.id)))));
      $$(".js-log-status", list).forEach((button) => button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await DMedAPI.log({ medication_id: Number(button.dataset.id), status: button.dataset.status });
          toast(`Medication logged as ${button.dataset.status}`);
        } catch (err) {
          toast(err.message, true);
        } finally {
          button.disabled = false;
        }
      }));
      $$(".js-update-status", list).forEach((select) => select.addEventListener("change", async () => {
        select.disabled = true;
        try {
          await DMedAPI.updateStatus(select.dataset.id, select.value);
          toast("Medication status updated");
          await render();
        } catch (err) {
          toast(err.message, true);
          await render();
        }
      }));
      $$(".js-delete", list).forEach((button) => button.addEventListener("click", async () => {
        if (!window.confirm("Delete this medication and its history?")) return;
        try { await DMedAPI.deleteMedication(button.dataset.id); toast("Medication deleted"); render(); } catch (err) { toast(err.message, true); }
      }));
    };
    $("#med-search")?.addEventListener("input", render);
    $("#add-medication")?.addEventListener("click", () => openMedicationModal());
    $("#close-modal")?.addEventListener("click", () => $("#med-modal").classList.add("hidden"));
    $("#med-modal")?.addEventListener("click", (event) => { if (event.target.id === "med-modal") event.currentTarget.classList.add("hidden"); });
    $("#medication-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      const save = $("#save-medication");
      save.disabled = true;
      try {
        const payload = medicationFormData(form);
        if (form.dataset.id) await DMedAPI.updateMedication(form.dataset.id, payload);
        else await DMedAPI.createMedication(payload);
        $("#med-modal").classList.add("hidden"); toast(form.dataset.id ? "Medication updated" : "Medication added"); render();
      } catch (err) { toast(err.message, true); } finally { save.disabled = false; }
    });
    try {
      await render();
      const editId = Number(new URLSearchParams(window.location.search).get("edit"));
      if (editId) {
        const meds = await DMedAPI.medications();
        const medication = meds.find((med) => med.id === editId);
        if (medication) openMedicationModal(medication);
      }
    } catch (err) { list.innerHTML = `<div class="empty-state">${escape(err.message)}</div>`; }
  }

  async function setupDetails() {
    if (!requireAuth()) return;
    setUserChrome();
    const id = Number(window.location.pathname.split("/").pop());
    try {
      const [med, logs, streak] = await Promise.all([DMedAPI.medication(id), DMedAPI.logs(id), DMedAPI.streak(id)]);
      $("#detail-name").textContent = med.name;
      $("#detail-description").textContent = med.description;
      $("#detail-status").innerHTML = statusBadge(med.status);
      $("#detail-dosage").textContent = med.dosage;
      $("#detail-frequency").textContent = title(med.frequency);
      $("#detail-start").textContent = date(med.start_date);
      $("#detail-end").textContent = date(med.end_date);
      $("#detail-progress").textContent = `${Math.min(100, Math.round(streak.completion_percentage || 0))}%`;
      $("#detail-progress-fill").style.width = `${Math.min(100, streak.completion_percentage || 0)}%`;
      $("#detail-streak").textContent = `${streak.current_streak || 0} days`;
      $("#detail-longest").textContent = `${streak.longest_streak || 0} days`;
      $("#detail-taken").textContent = streak.total_taken || 0;
      const history = $("#history-body");
      history.innerHTML = logs.length ? [...logs].reverse().map((log) => `<tr><td>${date(log.date)}</td><td>${statusBadge(log.status)}</td><td>${time(log.taken_at)}</td><td>${escape(log.notes || "—")}</td></tr>`).join("") :
        `<tr><td colspan="4" class="empty-state">No history logged yet.</td></tr>`;
      $("#detail-edit").onclick = () => { window.location.href = `/medications?edit=${id}`; };
      $("#detail-complete").onclick = async () => {
        try { await DMedAPI.updateStatus(id, med.status === "completed" ? "active" : "completed"); toast("Medication status updated"); setupDetails(); } catch (err) { toast(err.message, true); }
      };
      $("#detail-complete").textContent = med.status === "completed" ? "Reopen course" : "Mark complete";
    } catch (err) { $("#detail-error").textContent = err.message; $("#detail-error").classList.remove("hidden"); }
  }

  function setupSettings() {
    if (!requireAuth()) return;
    setUserChrome();
  }

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    if (page === "auth") setupAuth();
    if (page === "dashboard") setupDashboard();
    if (page === "medications") setupMedications();
    if (page === "detail") setupDetails();
    if (page === "settings") setupSettings();
  });
  return { toast, openMedicationModal };
})();
