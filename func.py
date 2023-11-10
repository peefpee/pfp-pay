from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo


class invoice:
    def __init__(self, invoice_id: int, address: str, amount: float, paid: bool):
        self.invoice_id = invoice_id
        self.address = address
        self.amount = amount
        self.paid = paid


class processor:
    client = None
    database = None
    invoice_collection = None

    def create_qrcode(self, amount: float, address: str):
        return f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=bitcoin:{address}?amount={amount}"

    def create_invoice(self, amount: float, address: str):
        id = self.invoice_collection.count_documents({}) + 1
        invoice = {
            "invoice_id": id,
            "address": address,
            "amount": amount
        }
        self.insert_mongo(invoice)

        return self.create_qrcode(amount, address), id

    def connect_mongo(self, url: str):
        self.client = MongoClient(url, server_api=ServerApi('1'))
        self.client.admin.command('ping')
        print("connected")
        return self.client

    def mongo_database(self, database_name: str):
        self.database = self.client[database_name]
        print(self.database)
        print(self.client)

    def mongo_collection(self, collection_name: str):
        self.invoice_collection = self.database[collection_name]

    def insert_mongo(self, data: dict):
        self.invoice_collection.insert_one(data)

    def find_mongo(self, data: dict):
        return self.invoice_collection.find(data)

    def count_mongo(self, collection=invoice_collection):
        print(collection)
        return collection.count_documents({})

    def add_invoice(self, invoicedata):
        data = {
            "invoice_id": invoicedata.invoice_id,
            "address": invoicedata.address,
            "amount": invoicedata.amount,
            "paid": invoicedata.paid
        }
        self.insert_mongo(data)
