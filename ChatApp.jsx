import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import "./App.css";

const SOCKET_SERVER_URL = process.env.REACT_APP_SOCKET_SERVER_URL;

const App = () => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [username, setUsername] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const socket = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (SOCKET_SERVER_URL) {
      socket.current = io(SOCKET_SERVER_URL);
  
      socket.current.on("receiveMessage", (message) => {
        setChat((prevChat) => [...prevChat, message]);
      });

      socket.current.on("receiveRecommendation", (recommendation) => {
        setChat((prevChat) => [...prevChat, `BookBot: ${recommendation}`]);
      });  
    }

    return () => {
      if (socket.current) {
        socket.current.off("receiveMessage");
        socket.current.off("receiveRecommendation");
        socket.current.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const handleInputChange = (e) => {
    setMessage(e.target.value);
  };

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const sendMessage = (e) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    const sanitizedMessage = sanitizedInput(trimmedMessage);
    if (sanitizedMessage && username.trim()) {
      socket.current.emit("sendMessage", `${username}: ${sanitizedMessage}`);
      setMessage("");
    }
  };

  const fetchBookRecommendations = () => {
    const mockRecommendation = `Recommended Book for '${searchTerm}': "The Adventures of Example Book"`;
    socket.current.emit("sendMessage", mockRecommendation);
    setSearchTerm("");
  };

  const sanitizedInput = (input) => {
    return input.replace(/<[^>]*>?/gm, '');
  };

  return (
    <div className="app">
      <header>
        <h1>BookBot</h1>
        <input 
          type="text" 
          value={username} 
          onChange={handleUsernameChange} 
          placeholder="Enter your username..." 
        />
      </header>
      <section className="chat-window">
        <ul>
          {chat.map((msg, index) => (
            <li key={index}>{msg}</li>
          ))}
          <div ref={chatEndRef} />
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
      <div className="book-search">
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder="Search for book recommendations..."
        />
        <button onClick={fetchBookRecommendations}>Search</button>
      </div>
    </div>
  );
};

export default App;