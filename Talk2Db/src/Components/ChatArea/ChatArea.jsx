import React, { useEffect, useState } from "react";
import "./ChatArea.css";
import InputBox from "./ChatComp/InputBox";
import Suggestions from "./ChatComp/Suggestion";
import Messages from "./ChatComp/Messages";
import useApiRequest from "../../Services/useApiRequest";
import { useNavigate, useParams } from "react-router-dom";
const ChatArea = ({ sidebarOpen }) => {
  const { request, loading, error, data } = useApiRequest();
  const { request: reqM, loading: loadM, error: errM } = useApiRequest();
  const navigate = useNavigate();
  const { id } = useParams();
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const fetchMessages = async () => {
      if (id) {
        try {
          const datam = await reqM(`/conversation/${id}`, "GET");
          console.log(datam);
          setMessages(datam);
        } catch (error) {
          console.error("Error fetching messages:", error);
        }
      } else {
        setMessages([]);
      }
    };
    fetchMessages();
  }, [id]);

  const handleSend = async () => {
    if (value.trim() !== "") {
      const newMessage = {
        id: new Date().getTime(),
        text: value,
        sender: "user",
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      const body = {
        query: value,
        conversation_id: id,
      };
      setValue("");

      try {
        const queryResponse = await request("/generate_sql", "POST", body);
        if (!queryResponse || !queryResponse.sql) {
          console.error("Failed to generate SQL query.");
          return;
        }

        // Detect response type
        const sqlText = queryResponse.sql.trim().toUpperCase();
        const isSQLQuery =
          sqlText.startsWith("SELECT") || sqlText.startsWith("SHOW");

        let botMessage;

        if (isSQLQuery) {
          botMessage = {
            id: new Date().getTime(),
            query: queryResponse.sql,
            sender: "bot",
            responseType: "query", // ✅ Mark as a SQL query response
          };
        } else {
          // If it's just a message, return it as is
          botMessage = {
            id: new Date().getTime(),
            query: queryResponse.sql, // The message content
            sender: "bot",
            responseType: "message", // ✅ Mark as a normal message response
          };
        }

        setMessages((prevMessages) => [...prevMessages, botMessage]);

        if (!id && queryResponse.conversation_id) {
          navigate(`/${queryResponse.conversation_id}`);
        }
      } catch (error) {
        console.error("Error processing query:", error);
      }
    }
  };

  const [shadow, setShadow] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setShadow(true);
      } else {
        setShadow(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className={`ChatArea ${sidebarOpen ? "" : "sidebar-closed"}`}>
      <div className="chat-pg">
        <div className="center">
          <nav className="chat-nav">
            <h1>
              TALK2<span>DB</span>
            </h1>
          </nav>
          {messages?.length > 0 ? (
            <Messages loading={loading} messages={messages} />
          ) : (
            <div className="chat-welcome">
              {/* <h1>Welcome to Talk2DB</h1> */}
              <p>
                Lets solve it <span>together !</span>, How can I help you ?
              </p>
              <Suggestions setInputValue={(text) => setValue(text)} />
            </div>
          )}

          <div className="chat-bottom">
            <InputBox
              value={value}
              onChange={(text) => {
                setValue(text);
              }}
              sendMessage={handleSend}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;
