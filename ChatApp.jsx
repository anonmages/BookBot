import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import "./App.css";
const SOCKET_SERVER_URL = process.env.REACT_APP_SOCKET_SERVER_URL;
const App = () => {
  const [message, setMessage] = useState(""); 
  const [chat, setChat] = useState([]); 
  const socket = io(SOCKET_SERVER_URL); 
  const handleInputChange = (e) => {
    setMessage(e.target.value);
  };
  const sendMessage = (e) => {
    e.preventDefault();
    if (message.trim()) {
      socket.emit("sendMessage", message); 
      setMessage("");
    }
  };
  useEffect(() => {
    socket.on("receiveMessage", (message) => {
      setChat((prevChat) => [...prevChat, message]);
    });
    return () => {
      socket.off("receiveMessage");
    };
  }, [socket]);
  return (
    <div className="app">
      <header>
        <h1>BookBot</h1>
      </header>
      <section className="chat-window">
        <ul>
          {chat.map((msg, index) => (
            <li key={index}>{msg}</li>
          ))}
        </ul>
      </section>
      <form className="message-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={message}
          onChange={handleInputChange}
          placeholder="Type a message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};
export default App;