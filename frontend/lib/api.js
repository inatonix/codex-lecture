const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function handleResponse(response) {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) {
        message = Array.isArray(body.detail)
          ? body.detail.map((item) => item.msg || item).join(", ")
          : body.detail;
      }
    } catch (error) {
      // response not json
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function fetchUsers() {
  const response = await fetch(`${BASE_URL}/users`);
  return handleResponse(response);
}

export async function createUser(payload) {
  const response = await fetch(`${BASE_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function updateUser(userId, payload) {
  const response = await fetch(`${BASE_URL}/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deleteUser(userId) {
  const response = await fetch(`${BASE_URL}/users/${userId}`, {
    method: "DELETE",
  });
  return handleResponse(response);
}
