const BASE = import.meta.env.VITE_API_URL;

// Funzione di supporto: gestisce risposta ed errori in un solo punto
async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    throw new Error(`Errore ${res.status} su ${path}`);
  }
  return res.json();
}

// TOTEM: elenco dei servizi
export function getServices() {
  return request("/services");                      // ← da verificare in /docs
}

// TOTEM: richiede un ticket per un servizio
export function createTicket(serviceId) {
  return request("/tickets", {                      // ← da verificare in /docs
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service_id: serviceId }),
  });
}

// OFFICER: chiama il prossimo cliente per il counter
export function callNext(counterId) {
  return request(`/counters/${counterId}/next`, {   // ← da verificare in /docs
    method: "POST",
  });
}

// DISPLAY: stato attuale (ticket chiamati e code)
export function getDisplayState() {
  return request("/display");                       // ← da verificare in /docs
}