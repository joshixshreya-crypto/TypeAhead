
const Autocomplete = ({ handleChange, inputVal }) => {
  return (
    <>
      <input
        value={inputVal}
        placeholder="select room or add a new room....."
        style={{
          height: "3rem",
          width: "20rem",
          border: "2px solid grey",
          padding: "0px 8px",
          justifyContent: 'center'
        }}
        onChange={handleChange}
      ></input>
    </>
  );
};

export default Autocomplete;
