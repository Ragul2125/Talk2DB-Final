import "./App.css";
import Login from "./Components/Login/Login";
import Popup from "./Components/Pop/PopUp";
import Home from "./Pages/Home";
import { BrowserRouter, Routes, Route } from "react-router-dom";
function App() {
  return (
    <BrowserRouter>
      {/* <Routes>
        <Route path="/" element={<Login/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/home" element={<Home />} />
        <Route path="/home/:id" element={<Home />} />
      </Routes> */}
      <Routes>
        {/* <Route path="/popup" element={<Popup />} /> */}
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/:id" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
