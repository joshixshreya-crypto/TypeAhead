import { useEffect, useMemo, useState } from "react";
import { startsWithInTrie } from "../restApi";
import debounce from "lodash.debounce";

const SuggestionList = ({ inputVal, handleSelectSuggestion }) => {
  const [suggList, setSuggList] = useState([]);
  const suggestionListApiDebounce = useMemo(() => {
    return debounce((val) => {
      startsWithInTrie(val)
        .then((res) => {
          setSuggList(res.data.response);
        })
        .catch((e) => {
          console.log(e);
        });
    }, 500);
  }, []);

  useEffect(() => {
    suggestionListApiDebounce(inputVal);
  }, [inputVal]);

  return (
    <>
      {suggList.map((data) => (
        <li
          style={{ listStyle: "none", cursor: "pointer" }}
          onMouseEnter={(e) => {
            e.target.style.background = "#f0f0f0";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "white";
          }}
          onClick={() => handleSelectSuggestion(data)}
        >
          {data}
        </li>
      ))}
    </>
  );
};

export default SuggestionList;
