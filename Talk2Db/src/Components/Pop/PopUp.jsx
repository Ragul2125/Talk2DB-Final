import { useState } from "react";
import "./Popup.css";
export default function DatabasePopup({setPopup}) {
  const [formData, setFormData] = useState({
    user: "root",
    password: "root",
    database: "talk2db",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Submitted credentials:", formData);
    // TODO: replace with real connection logic.
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
