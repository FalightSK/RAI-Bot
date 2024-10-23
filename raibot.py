from prompt_template import system_prompt
import pandas as pd
import json
from datetime import datetime
from openai import OpenAI
from Database import RetriveDoc, update_link, generate, get_link

class Agent_module:
    def __init__(self, name, system, openai_clien, temperature=0.1, need_mem=False):
        self.name : str = name
        self.system : str = system
        self.openai_clien = openai_clien
        self.temperature : float = temperature
        self.need_mem : bool = need_mem
        self.memory : dict = {'user':[],'assistant':[]}
    
    def reset_memory(self):
        self.memory = {'user':[],'assistant':[]}
        #print("Memory reseted")
        return "Memory reseted"
    
    def mwm(self, window_size=5):
        '''
        memory window management
        '''
        if len(self.memory['user'])>window_size:
            self.memory['user'] = self.memory['user'][-1*int(window_size):]
            self.memory['assistant'] = self.memory['assistant'][-1*int(window_size-1):]
        else:
            pass

    def respond(self, massages):
        if self.need_mem:
            self.mwm()
        response = self.openai_clien.chat.completions.create(
        model="typhoon-v1.5x-70b-instruct",
        messages=massages,
        max_tokens=700,
        temperature=self.temperature,
        top_p=0.9,
    )
        res = str(response.choices[0].message.content)
        if self.need_mem:
            self.memory['assistant'].append(res)
        return res

    def export_memory(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") 
        pd.DataFrame(self.memory).to_csv(f"{self.name}_memory_{now}.csv")
        print(f"Memory exported to {self.name}_memory_{now}.csv")
        res = f"Memory exported to {self.name}_memory_{now}.csv"
        return res
    

class Chat_Agent(Agent_module):
    def __init__(self, name, system, openai_clien, temperature=0.1):
        super().__init__(name, system, openai_clien, temperature)
    
    def set_input(self, user_input, memory_shunk):
        message = [{"role": "system", "content": str(self.system)}]
        for i in range(len(memory_shunk['assistant'])):
            message.append({"role": "user", "content": str(memory_shunk['user'][i])})
            message.append({"role": "assistant", "content": str(memory_shunk['assistant'][i])})

        message.append({"role": "user", "content": str(user_input)})  # Add the new message
        #self.memory['user'].append(str(user_input))  # Update memory
        return message

    def reponse_chat(self, user_input, memory_shunk):
        message = self.set_input(user_input, memory_shunk)
        if self.need_mem:
            self.memory['user'].append(user_input)
        response = self.respond(message)
        #self.memory['assistant'].append(response)
        #return self.chat_response(response)
        return response
    

class Query_Agent(Agent_module):
    def __init__(self, name, system, openai_clien, temperature=0.1, filename=None):
        super().__init__(name, system, openai_clien, temperature)
        self.RAG = RetriveDoc() if filename is None else RetriveDoc(filename) 
        #print(RAG.search("ต้องเรียนทั้งหมดกี่เครดิต")["topic"])
    
    def debug_res(self, user_input):
        message = [{"role": "system", "content": self.system},{"role": "user", "content": user_input}]
        self.memory['user'].append(str(user_input))
        response = self.respond(message)
        return response

    def reponse_rag(self, user_input):
        query = self.debug_res(user_input)
        print(query)
        rag_data = self.RAG.search(query)
        #print(rag_data['topic'])
        #print(rag_data.keys())
        try:
            information = rag_data['topic'] + ": "+ rag_data['detail'] + '\ncontact:' +rag_data['contact']
        except:
            information = rag_data['topic'] + ": "+ rag_data['detail'] + '\ncontact:' +rag_data['link'] + '\njob oppornity'+rag_data['job']

        self.memory['assistant'].append(query)
        #return self.chat_response(response)
        return information