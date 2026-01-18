import { Alert } from "@mui/material";
import { useEffect, useRef, useState } from "react";

const useSocketConnection = () => {
  const chatSocket = useRef(null);
  const [messages, setMessages] = useState([]);
  useEffect(() => {
    chatSocket.current = new WebSocket("ws://localhost:8000/ws");

    chatSocket.current.onopen = () => {
      console.log("connected to server");
    };

    chatSocket.current.onmessage = (event) => {
      
      const parsedData = JSON.parse(event.data)
      if(parsedData.error){
         console.warn(parsedData.error)
         return
      }
      console.log("=======>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",parsedData)
      setMessages((prev) => [...prev, parsedData]);
    };

    chatSocket.current.onerror = (error) => {
      console.log("websocket error", error);
    };

    return () => chatSocket.current.close();
  }, []);

  const sendMessage = (text, roomId , userId) => {
    console.log("userId" , userId)
    if (chatSocket.current?.readyState === WebSocket.OPEN) {
      const payload = {
        room_name: roomId,
        message: text,
        userId: userId
      };
      console.log("payload", payload);
      chatSocket.current.send(JSON.stringify(payload));
    }
  };

  return { messages, setMessages , sendMessage };
};

export default useSocketConnection;
