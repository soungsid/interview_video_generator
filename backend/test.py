from pymongo import MongoClient
client = MongoClient("mongodb+srv://soungsid:MFBfO3IKdE4RqbRd@cluster0.tmklvts.mongodb.net/?appName=Cluster0")
print(client.list_database_names())