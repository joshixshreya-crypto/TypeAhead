import { faker } from "@faker-js/faker";
import { Stack, Box, Avatar, TextField, Button } from "@mui/material";
import { useEffect, useState } from "react";
import useSocketConnection from "../socketConnection";
import { useParams } from "react-router-dom";
import { fetchMessageByRoomName } from "../restApi";

const ConversationComponent = () => {
  const [input, setInput] = useState("");
  const { messages, setMessages, sendMessage } = useSocketConnection();

  const { roomId } = useParams();
  const userId = sessionStorage.getItem("user_id")
  const formatTime = (isoTime) => {
    if (!isoTime) return "";
    return new Date(isoTime).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleSendMessage = () => {
    if (input.length > 0) {
      
      sendMessage(input, roomId, userId);
      setInput("");
      console.log("=====>messages", messages);
    } else {
      console.log("enter a message first");
      return;
    }
  };
  useEffect(() => {
    fetchMessageByRoomName(roomId)
      .then((res) => {
        console.log("room name", roomId);
        const messageHistory = res.data.result;
        // const prevMessage = res.data.result.map((m)=> m.message)
        setMessages(messageHistory);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [roomId]);

  return (
    <Stack height={"100%"} maxHeight={"100vh"}>
      {/* chat header */}
      <Box
        sx={{
          height: 100,
          width: "100%",
        }}
      >
        <Stack
          direction={"row"}
          sx={{
            alignItems: "center",
            alignContent: "center",
            padding: "10px",
            gap: "10px",
            color: "#1C1C1B",
          }}
        >
          <Avatar alt="image" src={faker.image.avatar()} />
          <h2 style={{ color: "darkgray" }}>USER A</h2>
        </Stack>
      </Box>
      {/* messages */}
      <Box
        width={"100%"}
        sx={{ flexGrow: 1, height: "74vh", overflow: "auto" }}
      >
        {messages.length > 0 &&
          messages.map((data) => {
            return (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  backgroundColor: "lightsteelblue",
                  borderRadius: "26px",
                  margin: "5px",
                  minHeight: "5rem",
                  padding: "3px",
                  alignItems: "flex-start",
                  wordBreak: "break-word",
                  opacity: "0.5",
                }}
              >
                <span
                  style={{
                    padding: "0px 15px",
                    // color: "black",
                    fontSize: "large",
                    fontWeight: "bolder",
                  }}
                >
                  {data.username}
                </span>
                <p
                  style={{ textAlign: "left", padding: "15px", color: "black" }}
                >
                  {data.message}
                </p>
                <span style={{ alignSelf: "flex-end", padding: "0px 8px" }}>
                  {formatTime(data.create_time)}
                </span>
              </Box>
            );
          })}
      </Box>
      {/* chat footer */}
      <Box
        sx={{
          height: 100,
          width: "100%",
          backgroundColor: "#E9E4D8",
        }}
      >
        <Stack direction={"row"}>
          <TextField
            value={input}
            height="4rem"
            fullWidth
            placeholder="write a message..."
            onChange={(e) => setInput(e.target.value)}
            variant="filled"
            InputProps={{
              disableUnderline: true,
            }}
          ></TextField>
          <Button onClick={handleSendMessage}>send</Button>
        </Stack>
      </Box>
    </Stack>
  );
};

export default ConversationComponent;
