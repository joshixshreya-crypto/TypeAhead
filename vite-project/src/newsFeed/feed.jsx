import { Box, IconButton, Stack, List } from '@mui/material'
import { useEffect, useState } from 'react'
import SearchFriends from './searchFriends';
import { useParams } from 'react-router-dom';
import { fetchNotifications } from '../restApi';
import NotificationsIcon from '@mui/icons-material/Notifications';
import Drawer from '@mui/material/Drawer';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { notificationEnum } from '../constants/notification';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import useSocketConnection from '../socketConnection';


const Feed = () => {
  const { userId } = useParams();
  const {} =  useSocketConnection()
  const [notificationsList, setNotificationsList] = useState([]);
  useEffect(() => {
    if (!userId) return;
    fetchNotifications(userId).then((res) => {
      console.log("notifications", res.data.response); 
      const notifications = res.data.response.filter((notificationsData =>notificationsData.notification_type === notificationEnum.FRIEND_REQUEST)).map((notificationsData)=>{
       
         return  {message: `Friend request from ${notificationsData.initiator_username}` ,request_id: notificationsData.request_id}
        
      })
      setNotificationsList(notifications)
    }).catch(e =>
      console.log((e))
    )
  }, [userId])

  // drawer state 
  const [state, setState] = useState({
    btn: false,
  });

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
            <ListItem key={notificationData.request_id} disablePadding>
              <ListItemButton>
                <ListItemIcon>
                  <PersonAddIcon/>
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