import { Button, Input, Stack } from "@mui/material";
import { useState } from "react";
import { addUser, loginUser } from "../restApi";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [userData, setUserData] = useState({
    username: "",
    password: "",
  });
  const navigate = useNavigate();

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setUserData((prev) => ({
      ...prev,
      [name]: value, // ask vaibhav
    }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    loginUser(userData)
      .then((res) => {
        const user_id = res.data.response.id
        sessionStorage.setItem("user_id", user_id)
        navigate(`/feed/${user_id}`)
        console.log("====>", res);
      })
      .catch((err) => {
        console.log(err);
      })
      .finally(() => {
        console.log("completed");
      });
    console.log(userData);
  };

  return (
    <div style={{ width: "30vw" }}>
      <h1>LOG IN </h1>
      <form onSubmit={handleFormSubmit}>
        <Stack sx={{ justifyContent: "center" }}>
          <Input
            name="username"
            onChange={handleFormChange}
            value={userData.username}
            sx={{ color: "white", borderBottom: "2px solid white" }}
            placeholder="enter username..."
          ></Input>
          <Input
            name="password"
            onChange={handleFormChange}
            value={userData.password}
            sx={{ color: "white", borderBottom: "2px solid white" }}
            placeholder="enter password..."
          ></Input>
          <Button type="submit" variant="primary">
            Log In
          </Button>
        </Stack>
      </form>
    </div>
  );
};

export default Login;
