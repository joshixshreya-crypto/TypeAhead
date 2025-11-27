
const Autocomplete = ({ handleChange, inputVal }) => {
  return (
    <>
      <input
        value={inputVal}
        placeholder="search here....."
        style={{
          height: "3rem",
          width: "20rem",
          border: "2px solid grey",
          padding: "0px 8px",
        }}
        onChange={handleChange}
      ></input>
    </>
  );
};

export default Autocomplete;
