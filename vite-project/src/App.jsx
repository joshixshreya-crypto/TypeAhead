import { useMemo, useState } from "react";
import "./App.css";
import Autocomplete from "./components/autocomplete";
import SuggestionList from "./components/suggestion-list";
import debounce from "lodash.debounce";

function App() {
  const [inputVal, setInputVal] = useState("");

  const handleDebounceInputVal = useMemo(
    () => debounce((input) => setInputVal(input), 300),
    []
  );

  const handleChange = (e) => {
    handleDebounceInputVal(e.target.value);
    // setInputVal(e.target.value)
  };

  const handleSelectSuggestion = (data) => {
    setInputVal(data);
  };

  return (
    <>
      <Autocomplete inputVal={inputVal} handleChange={handleChange} />
      {inputVal.length > 0 && (
        <SuggestionList
          inputVal={inputVal}
          handleSelectSuggestion={handleSelectSuggestion}
        ></SuggestionList>
      )}
    </>
  );
}

export default App;
