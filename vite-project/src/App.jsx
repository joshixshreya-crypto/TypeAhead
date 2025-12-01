import { useState } from "react";
import "./App.css";
import Autocomplete from "./components/autocomplete";
import SuggestionList from "./components/suggestion-list";
import { addSearchWordsToTrie } from "./restApi";

function App() {
  const [inputVal, setInputVal] = useState("");

  const handleChange = (e) => {
    setInputVal(e.target.value);
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

  const handleSearch = () =>{
    addSearchKeywordToTrie();
  }


  return (
    <>
      <Autocomplete inputVal={inputVal} handleChange={handleChange} />
      <button onClick={handleSearch}>Search</button>
      {inputVal.length > 0 && (
        <SuggestionList
          inputVal={inputVal}
          handleSelectSuggestion={handleChange}
        ></SuggestionList>

      )}
    </>
  );
}

export default App;
