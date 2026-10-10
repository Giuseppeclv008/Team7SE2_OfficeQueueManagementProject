import { useState } from "react";
import { callNextCustomer } from "../api/queueApi";
import BigButton from "../components/BigButton";

export default function Officer() {
  const [customer, setCustomer] = useState(null);
  const [queueEmpty, setQueueEmpty] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleNext() {
    setLoading(true);
    setError("");
    try {
      const next = await callNextCustomer();
      setCustomer(next);
      setQueueEmpty(next === null);
    } catch {
      setError("Couldn't call the next customer. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1>Counter</h1>

      <div className="card">
        {customer && (
          <>
            <p>Now serving</p>
            <div key={customer.id} className="huge-number pop">{customer.number}</div>
            <p>{customer.service}</p>
          </>
        )}
        {!customer && !queueEmpty && <p>No customer being served</p>}
        {queueEmpty && <p>No customers in the queue</p>}
      </div>

      {error && <p className="message-error" role="alert">{error}</p>}

      <BigButton
        label={loading ? "Calling..." : "Next customer"}
        onClick={handleNext}
        disabled={loading}
      />
    </main>
  );
}