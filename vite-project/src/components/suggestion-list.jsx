import { useEffect, useMemo, useState } from "react";
import { getFriendsList, startsWithInTrie } from "../restApi";
import debounce from "lodash.debounce";

const SuggestionList = ({ inputVal, handleSelectSuggestion, type = "room" }) => {
  console.log("propsss", inputVal, type)
  const [suggList, setSuggList] = useState([]);
  const suggestionListApiDebounce = useMemo(() => {
    return debounce((val) => {

      const apiCall = type === 'friend' ? getFriendsList(val) : startsWithInTrie(val)
      apiCall
        .then((res) => {
          console.log("suggestion list res", res)
          setSuggList(res.data.response);
        })
        .catch((e) => {
          console.log(e);
        });
    }, 500);

  }, []); 

  useEffect(() => {
    suggestionListApiDebounce(inputVal);
  }, [inputVal , type]);

  return (
    <div style={{ width: "21.22em" }}>
      {suggList.map((data) => {
        const username = typeof data === 'string'? data : data.children
        const user_id = typeof data === 'string'? data : data.user_id
        return(
        <li
          key = {user_id}
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
          {username}
        </li>
        )
      })}
    </div>
  );
};

export default SuggestionList;
