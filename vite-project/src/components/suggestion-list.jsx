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
    console.log("=====>",suggList)
  }, [inputVal]);

  return (
    <div style={{ width: "21.22em" }}>
      {suggList.map((data) => (
        <li
          style={{
            listStyle: "none",
            cursor: "pointer",
            backgroundColor: "grey",
            color: "black",
          }}
          onMouseEnter={(e) => {
            e.target.style.background = "#f0f0f0";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "grey";
          }}
          onClick={() => handleSelectSuggestion(data)}
        >
          {data}
        </li>
      ))}
    </div>
  );
};

export default SuggestionList;
