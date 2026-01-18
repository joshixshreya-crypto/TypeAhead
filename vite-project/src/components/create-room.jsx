import { useState } from "react";
import Autocomplete from "./autocomplete";
import SuggestionList from "./suggestion-list";
import { addSearchWordsToTrie } from "../restApi";
import { useNavigate, useParams } from "react-router-dom";

const CreateRoom = () => {
  const [inputVal, setInputVal] = useState("");
  const navigate = useNavigate();
  const {user_id}  = useParams()

  const handleChange = (e) => {
    console.log("selected", e);
    setInputVal(e);
  };
  //insert word to trie code
  const addSearchKeywordToTrie = () => {
    addSearchWordsToTrie(inputVal)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const handleSearch = () => {
    addSearchKeywordToTrie();
    console.log("user iddd====>",user_id)
    navigate(`/chat/${inputVal}`)
  };
  return (
    <div>
      <h1
        style={{
          textAlign: "center",
          fontSize: "2.3rem",
          fontWeight: 600,
          color: "fffff",
          textShadow: "0 0 10px rgba(0,0,0,0.08)",
          margin: "20px 0",
          letterSpacing: "1px",
        }}
      >
        Search your friends and chat with them !!
      </h1>
      <div style={{ position: "absolute" }}>
        <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
          <Autocomplete
            inputVal={inputVal}
            handleChange={(e) => handleChange(e.target.value)}
          />
          <button style={{ cursor: "pointer" }} onClick={handleSearch}>
            start
          </button>
        </div>
        {inputVal.length > 0 && (
          <SuggestionList
            inputVal={inputVal}
            handleSelectSuggestion={handleChange}
          ></SuggestionList>
        )}
      </div>
    </div>
  );
};

export default CreateRoom;
