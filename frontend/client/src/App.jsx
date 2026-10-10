import { BrowserRouter, Routes, Route } from "react-router-dom";
import Totem from "./pages/Totem";
import Officer from "./pages/Officer";
import DisplayPage from "./pages/DisplayPage";

export default function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Totem />} />
        <Route path="/officer" element={<Officer />} />
        <Route path="/display" element={<DisplayPage />} />
      </Routes>
    </BrowserRouter>
  )
}