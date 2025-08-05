import "./App.css";
import Login from "./Components/Login/Login";
import Home from "./Pages/Home";
import { BrowserRouter, Routes, Route } from "react-router-dom";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/home" element={<Home />} />
        <Route path="/home/:id" element={<Home />} />
      </Routes>
      {/* <Routes>

        <Route path="/home" element={<Home />} />
        <Route path="/home/:id" element={<Home />} />
      </Routes> */}
    </BrowserRouter>
  );
}

export default App;
