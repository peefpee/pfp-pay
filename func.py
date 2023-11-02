import qrcode
from datetime import datetime


class processor():
    def create_invoice(self, amount: float, address: str):
        return f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=bitcoin:{address}?amount={amount}"
