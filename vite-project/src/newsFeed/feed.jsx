import { Box, IconButton, Stack } from '@mui/material'
import React, { useEffect } from 'react'
import SearchIcon from '@mui/icons-material/Search';
import SearchFriends from './searchFriends';
import { useParams } from 'react-router-dom';
import { fetchNotifications } from '../restApi';


const Feed = () => {
  const {userId} = useParams();
  useEffect(() => {
    fetchNotifications(userId).then((res) => {
      console.log("notifications", res.data.response)
    }).catch(e =>
      console.log((e))
    )
  }, [])
  return (
    <Stack>
      <SearchFriends></SearchFriends>
    </Stack>
  )
}

export default Feed