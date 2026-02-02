import { Box, Stack } from '@mui/material'
import { useParams } from 'react-router-dom';
import { checkFriendRequestStatus, getFriendsList, respondToFriendRequest, sendFriendRequest } from '../restApi';
import { useEffect, useState } from 'react';
import { requestStatusEnum } from '../constants/notification';


const Profile = () => {
    const { username } = useParams();
    const friendUserId = sessionStorage.getItem("addFriendUserId");
    const userId = sessionStorage.getItem("user_id");
    const [status, setStatus] = useState(null);


    const handleAddFriendHandler = () => {
        if (buttonText() == 'ADD FRIEND') {
            sendFriendRequest(userId, friendUserId)
        }
        else if (buttonText() == 'ACCEPT REQUEST') {
            const payload = {
                user_id: userId,
                initiator_id: friendUserId
            }

            respondToFriendRequest(payload).then((res) => {
                setStatus(requestStatusEnum.ACCEPTED)
            }).catch(e => console.log(e))
        }

    }
    useEffect(() => {
        console.log("~~~~~~~", friendUserId)
        if (friendUserId) {
            checkFriendRequestStatus(userId, friendUserId).then((res) => {
                setStatus(res.data.status);
            }).catch(e => console.log(e))
        }

    }, [userId, friendUserId])

    const buttonText = () => {
        if (status === requestStatusEnum.SENT) {
            return "REQUEST SENT"
        }
        else if (status === requestStatusEnum.RECEIVED) {
            return 'ACCEPT REQUEST'
        }
        else if (status === requestStatusEnum.ACCEPTED) {
            return 'FRIENDS'
        }
        else {
            return 'ADD FRIEND'
        }
    }

    return (
        <Stack>
            <Box>
                <h3>{username}</h3>
            </Box>
            <Box>
                <button onClick={handleAddFriendHandler}>{buttonText()}</button>
                <button>Message</button>
            </Box>
            <Box>
                <h4>Posts</h4>
            </Box>
        </Stack>
    )
}

export default Profile