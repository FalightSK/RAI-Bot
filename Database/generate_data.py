from .utils.sheet2csv import convert_google_sheet_url
from .utils.embedding import Embedding

import re
import pandas as pd
import json

def generate(link: str, save_name: str = 'doc'):
    '''
    link : link from ggdrive
    save_name : name of the file to save (without .json)
    '''
    model = Embedding(r"sentence-transformers/xlm-r-distilroberta-base-paraphrase-v1")
    print(convert_google_sheet_url(link))
    df = pd.read_csv(convert_google_sheet_url(link))

    dataset = []

    if save_name == 'doc':
        for d in df.iloc:
            topic = re.sub("\n|\r|\t", " ", d["Topics"])
            detail = re.sub("\n|\r|\t", " ",d["Detail"])
            contact = re.sub("\n|\r|\t", " ",d["Contact_Source"])
            vector = model.forward(topic)
            dataset.append({"topic": topic, "detail": detail, "contact": contact, "vector": vector.tolist()})
    else:
        for d in df.iloc:
            topic = re.sub("\n|\r|\t", " ", d["Topic"])
            detail = re.sub("\n|\r|\t", " ",d["Detail"]) if type(d["Detail"]) == str else ""
            job = re.sub("\n|\r|\t", " ",d["JobOpportunities"]) if type(d["JobOpportunities"]) == str else ""
            link = re.sub("\n|\r|\t", " ",d["Link"]) if type(d["Link"]) == str else ""
            vector = model.forward(topic)
            dataset.append({"topic": topic, "detail": detail, "job": job, "link":link, "vector": vector.tolist()})
    
    with open(f"Database/{save_name}.json", "w") as jsonFile:
        jsonFile.write(json.dumps(dataset, ensure_ascii=False))
        pass
    
if __name__ == '__main__':
    
    pass