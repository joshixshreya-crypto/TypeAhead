const SuggestionList = ({ inputVal , handleSelectSuggestion }) => {
  const suggList = ["cat is good", "cat is bad", "catastrophy"];
  const newList = suggList.filter((data) => data.includes(inputVal));

 
  return (
    <>
      {newList.map((data) => (
        <li
          style={{ listStyle: "none" , cursor: "pointer" }}
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
