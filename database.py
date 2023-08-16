from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def connect(password):
    uri = "mongodb+srv://deleoadr:{}@mechycluster.1nt5uzp.mongodb.net/?retryWrites=true&w=majority".format(password)
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client
