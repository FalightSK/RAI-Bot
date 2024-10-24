from .utils.sheet2csv import convert_google_sheet_url
from .utils.embedding import Embedding

from llama_index.core.node_parser import SentenceSplitter
from transformers import AutoTokenizer

import re
import pandas as pd
import json

def chunking(sentences: str, chunksize: int, overlap: int) -> tuple[list[str], list[list]]:
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=0)
    sub_sentenses = parser.split_text(sentences)
    
    model = Embedding(r"BAAI/bge-m3")
    tokenizer = AutoTokenizer.from_pretrained(r'airesearch/LLaMa3-8b-WangchanX-sft-Full')
    tokens = []
    for s in sub_sentenses:
        tokens += tokenizer.tokenize(s.lower())
    
    # print(tokens)
    chunks, vectors = [], []
    for i in range(0, len(tokens), chunksize - overlap):
        sen2vec = "".join(tokens[i:i+chunksize])
        sen2vec = re.sub(r'▁', ' ', sen2vec)
        if i == 0:
            chunk = sen2vec
        else:
            chunk = "".join(tokens[i+overlap: i+chunksize])
            chunk = re.sub(r'▁', ' ', chunk)
        vector = model.forward(sen2vec)
        
        chunks.append(chunk)
        vectors.append(vector)
    
    return chunks, vectors

def generate(link: str, save_name: str = 'doc'):
    '''
    link : link from ggdrive
    save_name : name of the file to save (without .json)
    '''    
    print("##### SERVER LOG UPDATING LINK:", convert_google_sheet_url(link))
    
    df = pd.read_csv(convert_google_sheet_url(link))
    
    documents = ""
    contact_book = []
    if save_name == 'doc':
        for d in df.iloc:
            topic = re.sub("\n|\r|\t", " ", d["Topics"])
            detail = re.sub("\n|\r|\t", " ",d["Detail"])
            contact = re.sub("\n|\r|\t", " ",d["Contact_Source"])
            
            template = f"Topics: {topic} \nDetail: {detail} <eot>"
            documents = "\n".join([documents, template])
            contact_book.append(contact)
    
    chunks, vectors = chunking(documents, 128, 24)
    print(str(chunks).count("<eot>"))
    del documents, df
    # print("###########\n", chunks[3])
    # print("###########\n",chunks[4])
    # print(len(chunks))
    
    database = {}
    start_eot, total_eot = 0, 0
    for i, chunk in enumerate(chunks):
        len_split = len(chunk.split("<eot>"))
        if len_split > 1 and i != len(chunk)-1:
            start_eot = total_eot
            total_eot += len_split-1
        database[i] = {"content": chunk, "vector": vectors[i].tolist(), "contact": "\n".join(contact_book[start_eot:total_eot])}
    
    # print(database)
    
    with open(f"Database/{save_name}.json", "w") as jsonFile:
        jsonFile.write(json.dumps(database, ensure_ascii=False))
        pass
    
if __name__ == '__main__':
    pass