import { Box, IconButton, Stack, List } from '@mui/material'
import { useEffect, useState } from 'react'
import SearchFriends from './searchFriends';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchNotifications } from '../restApi';
import NotificationsIcon from '@mui/icons-material/Notifications';
import Drawer from '@mui/material/Drawer';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import useSocketConnection from '../socketConnection';
import { notificationEnum } from '../constants/notification';

const Feed = () => {
  const { userId } = useParams();
  const { messages} = useSocketConnection();
  const [notificationsList, setNotificationsList] = useState([]);
  const navigate = useNavigate();
  useEffect(() => {
    if (!userId) return;
    fetchNotifications(userId).then((res) => {
      console.log("notifications", res.data.response);
      const notifications = res.data.response.filter((notificationsData => notificationsData.notification_type === notificationEnum.FRIEND_REQUEST)).map((notificationsData) => {

        return { ...notificationsData,message: `Friend request from ${notificationsData.initiator_username}` }

      })
      setNotificationsList(notifications)
    }).catch(e =>
      console.log((e))
    )
  }, [userId])

  useEffect(() => {
    if(!messages || messages.length ===0) return;
    console.log("heyyyy",messages)
    const last = messages[messages.length - 1];
    if(last.notification_type !== notificationEnum.FRIEND_REQUEST) return;  

    setNotificationsList((prev)=>
    [
      ...prev,
      {
        ...last, 
        message: `Friend request from ${last.initiator_username}`,
      }

    ])
   
  },[messages])

  // drawer state 
  const [state, setState] = useState({
    btn: false,
  });

  const username = sessionStorage.getItem("username");

  const toggleDrawer =
    (anchor, open) => (event) => {
      if (
        event?.type === 'keydown' &&
        (event.key === 'Tab' || event.key === 'Shift')
      ) {
        return;
      }
      setState({ ...state, [anchor]: open });
    };
  function handleNotificationClick(initiatorData) {
     sessionStorage.setItem("addFriendUserId", initiatorData.initiator_id);
    sessionStorage.setItem("addFriendUsername", initiatorData.initiator_username);
    navigate(`/profile/${initiatorData.initiator_username}`)
  }
  // notifications list 
  const list = (event) => {
    return (
      <Box
        sx={{ width: 250 }}
        role="presentation"
        onClick={toggleDrawer(event, false)}
        onKeyDown={toggleDrawer(event, false)}
      >
        <List>
          {notificationsList.map((notificationData, index) => (
            <ListItem onClick = {()=> handleNotificationClick(notificationData)} key={notificationData.request_id} disablePadding>
              <ListItemButton>
                <ListItemIcon>
                  <PersonAddIcon />
                </ListItemIcon>
                <ListItemText primary={notificationData.message} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    )
  }

  return (
    <Stack>
      <h2>{username}</h2>
      <SearchFriends></SearchFriends>
      <Box sx={{ position: 'absolute', top: 10, right: 10 }}>
        <div>
          <IconButton onClick={toggleDrawer('btn', true)}>
            <NotificationsIcon />
          </IconButton>
          <Drawer
            anchor='right'
            open={state['btn']}
            onClose={toggleDrawer('btn', false)}
          >
            {list('btn')}
          </Drawer>

        </div>

      </Box>
    </Stack>
  )
}

export default Feed