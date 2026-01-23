
import axios from "axios"
const apiClient = axios.create({
  baseURL: "http://localhost:8000",
});

export const addSearchWordsToTrie = (searchPayload) =>{
    console.log("searchPayload",searchPayload);
   return  apiClient.post('/insert-trie' ,{word: searchPayload});

}

export const searchWordInTrie = (searchPayload) =>{
    console.log("searchhh" , searchPayload)
    return apiClient.get(`/search-trie/${searchPayload}`);
}

export const startsWithInTrie = (prefix) =>{
    return apiClient.get(`/starts-with/${prefix}`)
}

//chat apis
export const fetchMessageByRoomName = (room_name) =>{
    return apiClient.get(`/fetch-chats/${room_name}`)
}

//add user
export const addUser = (userPayload) =>{
    return apiClient.post('/user-creds' , userPayload)
}

// login user
export const loginUser = (loginPayload) =>{
    return apiClient.post('/login' , loginPayload)
}
// search friends and add them as friends
export const getFriendsList = (prefix) =>{
    console.log("getting friends list for prefix:", prefix)
    return apiClient.get(`/starts-with-users/${prefix}`)
}

// send request to add friend

export const sendFriendRequest = (initiator_id , reciever_id)=>{
    return apiClient.post(`/send-friend_request` , {initiator_id: initiator_id , reciever_id: reciever_id})
}

//fetch notifications
export const fetchNotifications = (user_id) =>{
    return apiClient.get(`/fetch-notifications/${user_id}`)

}