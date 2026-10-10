import BigButton from "../components/BigButton";

export default function Totem() {
  return (
    <div className="page">
      <h1>Totem</h1>
      <BigButton label="Prova" onClick={() => alert("Click!")} />
      <BigButton label="Disabilitato" disabled />
    </div>
  );
}