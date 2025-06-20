import React, { useEffect } from "react";
import "./SideNav.css";
import { LuPanelLeftClose, LuPanelRightClose, LuLogOut } from "react-icons/lu";
import { HiOutlinePencilAlt } from "react-icons/hi";
import profileImg from "../../assets/profile_img.jpg";
import History from "./Comp/History";
import { useNavigate } from "react-router-dom";

const SideNav = ({ isOpen, setIsOpen }) => {
  const navigate = useNavigate();
  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };
  console.log(isOpen)
  return (
    <>
      {/* Toggle Button (Only shown when sidebar is closed) */}
      {!isOpen && (
        <button className="sidebar-toggle-btn" onClick={toggleSidebar}>
          <LuPanelRightClose />
        </button>
      )}

      {/* Overlay (Visible only when sidebar is open) */}
      {isOpen && <div className="overlay" onClick={toggleSidebar}></div>}

      {/* Sidebar */}
      <div className={`Sidebar ${isOpen ? "open" : "closed"}`}>
        <div className="sideNav-top">
          <header>
            <div className="close" onClick={toggleSidebar}>
              <LuPanelLeftClose />
            </div>
            <div
              onClick={() => {
                navigate("/");
              }}
              className="new-chat"
            >
              <HiOutlinePencilAlt />
            </div>
          </header>
          <div className="his">
            <History />
          </div>
        </div>

        {/* Profile Section */}
        <div className="profile">
          <div className="profile-img">
            <img src={profileImg} alt="Profile" />
          </div>
          <div className="user-name">
            <p>Adela Parkson</p>
          </div>
          <div className="logout-btn">
            <LuLogOut />
          </div>
        </div>
      </div>
    </>
  );
};

export default SideNav;
