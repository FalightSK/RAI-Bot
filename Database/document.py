from .utils.embedding import Embedding

import torch
from sklearn.metrics.pairwise import cosine_similarity

import json


class RetriveDoc:
    def __init__(self, name: str = "doc"):
        self.model = Embedding(r"sentence-transformers/xlm-r-distilroberta-base-paraphrase-v1")
        
        with open(f"Database/{name}.json", "r") as JsonFile:
            self.doc = json.loads(JsonFile.read())
    
    def search(self, inputs):
        vector = self.model.forward(inputs)
        
        index = -1
        dis = -1e9
        for i, d in enumerate(self.doc):
            temp = cosine_similarity([vector], [d["vector"]])
            if temp > dis:
                dis = temp[0]
                index = i
        
        return self.doc[index]
    
# How to use
if __name__ == '__main__':
    RAG = RetriveDoc()
    print(RAG.search("ต้องเรียนทั้งหมดกี่เครดิต")["topic"])
    