from .utils.embedding import Embedding

from sklearn.metrics.pairwise import cosine_similarity

import json

class RetriveDoc:
    def __init__(self, name: str = "doc"):
        self.model = Embedding(r"BAAI/bge-m3")
        
        with open(f"Database/{name}.json", "r") as JsonFile:
            self.doc = json.loads(JsonFile.read())
    
    def search(self, inputs, top_k=5) -> str:
        vector = self.model.forward(inputs)
        results = []
        for i, (k, d) in enumerate(self.doc.items()):
            dist = cosine_similarity([vector], [d["vector"]])
            results.append([dist, i])
        
        results.sort(reverse=True)
        indexes = results[:top_k]
        indexes = sorted(indexes, key=lambda x:x[1])
        
        knowledge = ""
        for _, i in indexes:
            knowledge += "\n".join([self.doc[str(i)]["content"], self.doc[str(i)]["contact"]])
        
        return knowledge
    
# How to use
if __name__ == '__main__':
    RAG = RetriveDoc()
    print(RAG.search("ต้องเรียนทั้งหมดกี่เครดิต"))
    