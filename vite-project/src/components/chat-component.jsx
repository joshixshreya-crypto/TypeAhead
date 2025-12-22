import React from 'react'
import {Stack , Box} from '@mui/material'
import ConversationComponent from './conversation-component'

const ChatComponent = () => {
  return (
      <Stack>
        <Box sx= {{height: '100%' , width: '97vw'}}>
          <ConversationComponent></ConversationComponent>
        </Box>
      </Stack>
  )
}

export default ChatComponent