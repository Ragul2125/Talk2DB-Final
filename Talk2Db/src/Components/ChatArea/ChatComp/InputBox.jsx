import { useState, useRef, useEffect } from "react";
import { FaArrowRight } from "react-icons/fa6";
import { RiMic2Line, RiVoiceprintFill } from "react-icons/ri";

const InputBox = ({ value, onChange, sendMessage }) => {
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef(null);
  const recognition =
    "SpeechRecognition" in window || "webkitSpeechRecognition" in window
      ? new (window.SpeechRecognition || window.webkitSpeechRecognition)()
      : null;

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset height to auto to calculate the correct scroll height
      textarea.style.height = "auto";

      // Calculate the scroll height
      const scrollHeight = textarea.scrollHeight;

      // Set height with min and max constraints
      const newHeight = Math.min(
        Math.max(scrollHeight, 48), // Minimum height of 48px
        150 // Maximum height of 150px
      );

      textarea.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [value]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (recognition) {
    recognition.continuous = false;
    recognition.interimResults = false;
  }

  const handleMicClick = () => {
    if (!recognition) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    if (!isRecording) {
      recognition.start();
      setIsRecording(true);
    } else {
      recognition.stop();
      setIsRecording(false);
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onChange(transcript);
    };

    recognition.onspeechend = () => {
      setIsRecording(false);
      recognition.stop();
    };

    recognition.onerror = () => {
      setIsRecording(false);
    };
  };

  return (
    <div className="chat-container">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="chat-input-box"
      >
        <textarea
          ref={textareaRef}
          placeholder="Ask here..."
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
          }}
          onKeyDown={handleKeyDown}
          rows={1}
          style={{
            minHeight: "48px",
            maxHeight: "150px",
            overflowY: value.length > 0 ? "auto" : "hidden",
          }}
        />
        <button
          type="button"
          className="chat-mic-button"
          onClick={handleMicClick}
        >
          {isRecording ? (
            <RiVoiceprintFill className="breathing-animation" size={22} />
          ) : (
            <RiMic2Line size={22} />
          )}
        </button>
        <button
          className="chat-send-button"
          type="submit"
          disabled={value.trim() === ""}
        >
          <FaArrowRight size={22} />
        </button>
      </form>
    </div>
  );
};

export default InputBox;
