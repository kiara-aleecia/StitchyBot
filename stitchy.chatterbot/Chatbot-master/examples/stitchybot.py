# run with py -3.7 
from chatterbot import ChatBot
#from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from custom_list import *
from chatterbot.storage import UserModel
import logging  
import re

# class User():
#     def __init__(self, name, likes, dislikes):
#         self.name = name
#         self.likes = likes
#         self.dislikes = dislikes
        
#     def display(self):
#         print(f"About {self.name}")
#         print(f"\t{self.likes}")
#         print(f"\t{self.dislikes}")

chatbot = ChatBot("Stitchy", logic_adapters=[
        'chatterbot.logic.BestMatch'
    ],)

#chatbot = ChatBot("Stitchy")

logger = logging.getLogger() 
logger.setLevel(logging.CRITICAL)

crochet_corp = clean_corpus('kb_texts_c/')
#print(crochet_corp[:5])
knitting_corp = clean_corpus('kb_texts_k/')
full_corp = crochet_corp.append(knitting_corp)

#trainer = ListTrainer(chatbot)
#trainer.train(crochet_corp)
#trainer.train(knitting_corp)
# trainer.train([
#     "Hi",
#     "Welcome, friend 🤗",
# ])
# trainer.train([
#     "Are you a plant?",
#     "No, I'm the pot below the plant!",
# ])

#Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

#Train the chatbot based on the english corpus
#trainer.train("chatterbot.corpus.english")

#Train based on english greetings corpus
#trainer.train("chatterbot.corpus.english.greetings")
trainer.train("chatterbot.corpus.custom.crochet")
trainer.train("chatterbot.corpus.custom.knitting")

exit_conditions = (":q", "quit", "exit")
query = input("🧶 Stitchy: Please enter your name\n🗣️  ???:")
if len(query) == 0:
    query = 'Nobody'
user = UserModel(query)
print(f"🧶 : {chatbot.get_response(query)}")

while True:
    query = input(f"🗣️  {user.name}:")
    if re.search(r"^(I (understand|learned|know))", query):
        user.addSkill(query)
        print(f"🧶 Stitchy: {chatbot.get_response(query)}")
    if query in exit_conditions:
        break
    else:
        print(f"🧶 Stitchy: {chatbot.get_response(query)}")
        
# Create a new trainer for the chatbot
# trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the english corpus
# trainer.train("chatterbot.corpus.english")

# Train based on english greetings corpus
# trainer.train("chatterbot.corpus.english.greetings")

# Train based on the english conversations corpus
# trainer.train("chatterbot.corpus.english.conversations")

# Get a response to an input statement
# chatbot.get_response("Hello, how are you today?")

