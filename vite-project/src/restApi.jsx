
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