import { Route, Routes } from "react-router-dom";
import CreateRoom from "./components/create-room";
import ChatComponent from "./components/chat-component";
import "./App.css";
import Register from "./components/register";
import Feed from "./newsFeed/feed";
import Profile from "./newsFeed/profile";
import Login from "./components/login";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Register></Register>}></Route>
      <Route path="/create-room/:userId" element={<CreateRoom></CreateRoom>}></Route>
      <Route
        path="/chat/:roomId"
        element={<ChatComponent></ChatComponent>}
      ></Route>
       <Route
        path="/feed/:userId"
        element={<Feed></Feed>}
      ></Route>
       <Route
        path="/profile/:username"
        element = {<Profile/>}
      ></Route>
       <Route
        path="/login"
        element = {<Login/>}
      ></Route>
      
    </Routes>
  );
}

export default App;
