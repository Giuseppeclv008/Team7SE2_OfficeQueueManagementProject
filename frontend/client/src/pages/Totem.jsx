import { useEffect, useState } from "react";
import BigButton from "../components/BigButton";
import { createTicket } from "../api/api";
import { SERVICES } from "../config/services";

const TICKET_SCREEN_MS = 8000;  

export default function Totem() {
  const [ticket, setTicket] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!ticket) return;
    const id = setTimeout(() => setTicket(null), TICKET_SCREEN_MS);
    return () => clearTimeout(id);  
  }, [ticket]);

  async function handleClick(service) {
    if (busy) return;               
    setBusy(true);
    setError("");
    try {
      const newTicket = await createTicket(service.type);
      setTicket({ ...newTicket, serviceLabel: service.label });
    } catch {
      setError("Non è stato possibile emettere il ticket. Riprova.");
    } finally {
      setBusy(false);
    }
  }

  if (ticket) {
    return (
      <div className="page">
        <h1>Your Ticket</h1>
        <div className="card">
          <div className="huge-number">{formatCode(ticket.code)}</div>
          <p>{ticket.serviceLabel}</p>
        </div>
        <p>Wait to be called on the screen</p>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Choose a Service</h1>
      {error && (
        <p className="message-error" role="alert">
          {error}
        </p>
      )}
      <div className="button-grid">
        {SERVICES.map((s) => (
          <BigButton
            key={s.type}
            label={s.label}
            onClick={() => handleClick(s)}
            disabled={busy}
          />
        ))}
      </div>
    </div>
  );
}