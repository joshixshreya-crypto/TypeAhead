import { Box, IconButton } from '@mui/material'
import { useState } from 'react'
import SearchIcon from '@mui/icons-material/Search';
import SuggestionList from '../components/suggestion-list';
import { useNavigate } from 'react-router-dom';


const SearchFriends = () => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState("");
  function handleSubmit(e) {
    e.preventDefault()
    console.log(searchText)
  }

  function handleChange(fieldVal) {
    setSearchText(fieldVal)
  }

  function handleNavigateProfile(data) {
    console.log("msjdj" , data)
    sessionStorage.setItem("addFriendUserId" , data.user_id)
    sessionStorage.setItem("addFriendUsername" , data.children)
    navigate(`/profile/${data.children}`)
  }

  return (
    <Box >
      <form onSubmit={handleSubmit}>
        <input value={searchText} onChange={(e) => handleChange(e.target.value)} type="text" placeholder="Search friends..." />
        <IconButton type='submit'><SearchIcon /></IconButton>
        {
          searchText && searchText.trim().length > 0 && <SuggestionList inputVal={searchText} handleSelectSuggestion={handleNavigateProfile} type='friend'></SuggestionList>
        }

      </form>
    </Box>
  )
}

export default SearchFriends