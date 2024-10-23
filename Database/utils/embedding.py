import torch
from sentence_transformers import SentenceTransformer

class Embedding:
    def __init__(self, PATH):
        self.model = SentenceTransformer(PATH)
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")

    def forward(self, sentence):
        return self.model.encode(sentence)