import { Route, Routes } from "react-router-dom";
import CreateRoom from "./components/create-room";
import ChatComponent from "./components/chat-component";
import "./App.css";
import Register from "./components/register";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Register></Register>}></Route>
      <Route path="/create-room/:userId" element={<CreateRoom></CreateRoom>}></Route>
      <Route
        path="/chat/:roomId"
        element={<ChatComponent></ChatComponent>}
      ></Route>
    </Routes>
  );
}

export default App;
