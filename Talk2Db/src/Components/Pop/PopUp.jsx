import { useState } from "react";
import "./Popup.css";
import axios from "axios";
export default function DatabasePopup({setPopup}) {
  const [formData, setFormData] = useState({
    user: "root",
    password: "root",
    database: "talk2db",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };


const handleSubmit = async (e) => {
  e.preventDefault();
  console.log("Submitted credentials:", formData);

  try {
    const response = await axios.post("http://127.0.0.1:8000/connectdb", formData, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log("✅ Connected:", response.data);
    alert("Database connected successfully!");
    setPopup(false); // close popup
  } catch (error) {
    console.error("❌ Connection failed:", error.response?.data || error.message);
    alert("Failed to connect to database: " + (error.response?.data?.error || error.message));
  }
};


  return (
    <div className="popup-overlay">
      <div className="popup-card">
        <h2 className="popup-title">Database Credentials</h2>

        <form onSubmit={handleSubmit}>
          {/* User */}
          <div className="form-group">
            <label htmlFor="user">Database User Name</label>
            <input
              id="user"
              name="user"
              type="text"
              value={formData.user}
              onChange={handleChange}
              className="form-control"
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Database Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="form-control"
            />
          </div>

          {/* Database */}
          <div className="form-group">
            <label htmlFor="database">Database Name</label>
            <input
              id="database"
              name="database"
              type="text"
              value={formData.database}
              onChange={handleChange}
              className="form-control"
            />
          </div>

          <div className="btn">
          <button type="submit" className="btn-cancel" onClick={()=>{setPopup(false)}} >
            Cancel
          </button>
          <button type="submit" className="btn-primary" >
            Connect
          </button>
          </div>
        </form>
      </div>
    </div>
  );
}
