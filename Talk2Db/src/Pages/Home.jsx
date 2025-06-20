import React, { useState } from "react";
import "./Pages.css";
import SideNav from "../Components/SideNav/SideNav";
import ChatArea from "../Components/ChatArea/ChatArea";

const Home = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="Homepg">
      <SideNav isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <ChatArea sidebarOpen={sidebarOpen} />
    </div>
  );
};

export default Home;
