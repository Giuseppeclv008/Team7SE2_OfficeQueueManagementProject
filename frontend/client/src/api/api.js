const BASE = import.meta.env.VITE_API_URL;

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    throw new Error(`Errore ${res.status} su ${path}`);
  }
  return res.json();
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// ───────── TOTEM: creazione ticket ─────────
export function createTicket(serviceType) {
  return request("/tickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service_type: serviceType }),
  });
}

