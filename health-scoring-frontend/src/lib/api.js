const SYS_API_BASE =
  import.meta.env.VITE_SYS_API_BASE_URL || "http://127.0.0.1:8000";
const DATA_API_BASE =
  import.meta.env.VITE_DATA_API_BASE_URL || "http://127.0.0.1:8001";

async function parseJsonResponse(response, fallbackMessage) {
  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || fallbackMessage);
  }

  return data;
}

export async function loginUser({ id, pw }) {
  const response = await fetch(`${SYS_API_BASE}/api/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ id, pw }),
  });

  const data = await parseJsonResponse(response, "Unable to sign in.");

  if (!data?.user_uuid) {
    throw new Error(data?.message || "Unable to sign in.");
  }

  return data;
}

export async function createUser({ id, pw, first, last }) {
  const response = await fetch(`${SYS_API_BASE}/api/new_user/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ id, pw, first, last }),
  });

  const data = await parseJsonResponse(response, "Unable to create account.");

  if (!data?.user_uuid) {
    throw new Error(data?.message || "Unable to create account.");
  }

  return data;
}

export async function fetchWelcome() {
  const response = await fetch(`${SYS_API_BASE}/api/welcome/`);
  return parseJsonResponse(response, "Unable to load welcome message.");
}

export async function fetchUserHealth(user_uuid) {
  const response = await fetch(`${SYS_API_BASE}/api/bring/user_health_info/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_uuid }),
  });

  return parseJsonResponse(response, "Unable to load health profile.");
}

export async function updateUserHealth(payload) {
  const response = await fetch(`${SYS_API_BASE}/api/update/user_health_info/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse(response, "Unable to save health profile.");
}

export async function predictHealth(payload) {
  const formData = new FormData();

  Object.entries(payload).forEach(([key, value]) => {
    formData.append(key, String(value));
  });

  const response = await fetch(`${DATA_API_BASE}/api/predict`, {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse(response, "Unable to generate prediction.");
}

export async function createDashboard(payload) {
  const response = await fetch(`${DATA_API_BASE}/api/user/create_dashboard`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse(response, "Unable to create dashboard.");
}
