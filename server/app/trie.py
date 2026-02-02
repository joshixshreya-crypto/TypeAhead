from typing import Dict, Optional


class trie_node:
    def __init__(self):
        self.children: Dict[str , "trie_node"] = {}
        self.is_end: bool =  False
        self.user_id: str = ""
        # self.frequency: int = 0

class Trie:
    def __init__(self):
        self.root = trie_node()

    def insert(self , word:str , id: Optional[str] = None):
        curr = self.root
        for c in word:
            if c not in curr.children:
                curr.children[c] = trie_node()
            curr = curr.children[c]
        curr.is_end = True
        if(id):
            curr.user_id = id

    def search(self , word: str):
        curr = self.root
        for c in word:
            if c not in curr.children:
                return False
            curr = curr.children[c]
        return curr.is_end
    
    def starts_with(self , prefix: str):
        cur = self.root
        for c in prefix:
            if c not in cur.children:
                return []
            cur = cur.children[c]
        result = []
        self._dfs(cur , prefix , result)
        return result

    def _dfs(self , cur , prefix , result):
        if(cur.is_end == True):
            result.append({
                "children": prefix,
                "user_id":  cur.user_id
            })
        for key , node in cur.children.items():
            self._dfs(node , prefix+ key , result)
    
    

