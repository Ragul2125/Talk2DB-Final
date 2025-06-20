import { useEffect, useRef, useState } from "react";
import Table from "./Table";

const Messages = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);
  const [loadingMessageId, setLoadingMessageId] = useState(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (loading) {
      // Set loadingMessageId to the last user's message ID
      const lastUserMessage = messages
        .filter((msg) => msg.sender === "user")
        .pop();
      if (lastUserMessage) {
        setLoadingMessageId(lastUserMessage.id);
      }
    } else {
      setLoadingMessageId(null);
    }
  }, [loading, messages]);

  return (
    <div className="messages">
      {messages.map((message) => (
        <div className="message-wrapper" key={message.id}>
          {message.sender === "user" ? (
            <div className="message user-message">{message.text}</div>
          ) : message.responseType === "query" ? (
            <Table query={message.query} />
          ) : (
            <div className="message bot-message">{message.query}</div>
          )}
        </div>
      ))}

      {/* Show the loader only when waiting for bot response */}
      {loading && (
        <div className="dot-loader-container">
          <span className="dot-loader"></span>
          <span className="dot-loader"></span>
          <span className="dot-loader"></span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default Messages;
