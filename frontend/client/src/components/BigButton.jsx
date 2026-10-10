import "./BigButton.css";

export default function BigButton({ label, onClick, disabled = false }) {
  return (
    <button className="big-button" onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}