import { Box, Stack } from '@mui/material'
import { useParams } from 'react-router-dom';
import { sendFriendRequest } from '../restApi';


const Profile = () => {
    const { username } = useParams();
    const friendUserId = sessionStorage.getItem("addFriendUserId");
    const userId = sessionStorage.getItem("user_id");

    const handleAddFriendHandler = () => {
        sendFriendRequest(userId , friendUserId).then((res)=>{
            console.log("friend reques sent" , res.data.response)
        })
    }

    return (
        <Stack>
            <Box>
                <h3>{username}</h3>
            </Box>
            <Box>
                <button onClick={handleAddFriendHandler}>Add Friend</button>
                <button>Message</button>
            </Box>
            <Box>
                <h4>Posts</h4>
            </Box>
        </Stack>
    )
}

export default Profile