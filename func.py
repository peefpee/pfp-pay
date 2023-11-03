import qrcode
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo

class processor:
    client = None
    database = None
    invoice_collection = None
    def create_invoice(self, amount: float, address: str):
        return f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=bitcoin:{address}?amount={amount}"

    def connect_mongo(self, url: str):
        self.client = MongoClient(url, server_api=ServerApi('1'))
        self.client.admin.command('ping')
        print("connected")
        return self.client


    def mongo_database(self,database_name:str,client:pymongo.mongo_client.MongoClient=self.client):
        self.database=client[database_name]
    def mongo_collection(self,collection_name:str,client:pymongo.mongo_client.MongoClient=self.client):
        self.invoice_collection=self.database[collection_name]
    def insert_mongo(self,data:dict,col:pymongo.collection.Collection=invoice_collection):
        col.insert_one(data)

