import { BrowserRouter, Routes, Route } from "react-router-dom";
import Totem from "./pages/Totem";
import Officer from "./pages/Officer";

export default function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Totem />} />
        <Route path="/officer" element={<Officer />} />
      </Routes>
    </BrowserRouter>
  )
}