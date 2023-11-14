import json

from bson.json_util import dumps
from flask import *
from flask import request

import func
import requests

config = json.load(open('config.json'))
app = Flask(__name__)
app.func = func.processor()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/pay')
def pay():
    return render_template('pay.html')


@app.route('/payinvoice')
def payinvoice():
    return 'Go to /payinvoice/<invoiceid>', 301


@app.route('/pay/create', methods=["GET"])
def paycreate():
    addy = request.args.get('address', type=str)
    url = f"http://127.0.0.1:5000/{url_for('apicheckbtc',addy=addy)}"
    print(url)
    if not requests.get(url).json()["Success"]:
        return {"Success": "False", "Error": "Invalid Address"}, 401
    invoice = func.invoice(app.func.count_mongo(app.func.invoice_collection) + 1, addy,
                           request.args.get('amount', type=float), False)
    app.func.add_invoice(invoice)
    return redirect(f'{url_for("payinvoice")}/{invoice.invoice_id}')


@app.route('/payinvoice/<invoiceid>')
def payinvoiceid(invoiceid):
    invoiceid = int(invoiceid)
    if invoiceid > app.func.count_mongo(app.func.invoice_collection):
        return '404', 404
    dataa = list(app.func.find_mongo({"invoice_id": invoiceid}))
    data = json.loads(dumps(dataa, indent=2))[0]
    if data["paid"]:
        return render_template("paid.html")
    return render_template("payment.html", image_url=app.func.create_qrcode(data["amount"], data["address"]),
                           invoiceid=invoiceid, amount=data["amount"],
                           address=data["address"])


@app.route('/test/pay')
def testpay():
    invoice = func.invoice(app.func.count_mongo(app.func.invoice_collection), "test", 1, True)
    print(invoice.invoice_id)
    return invoice.address


@app.route('/test/create_invoice')
def testcreateinvoice():
    invoice = func.invoice(app.func.count_mongo(app.func.invoice_collection) + 1, request.args.get('address', type=str),
                           request.args.get('amount', type=float), False)
    app.func.add_invoice(invoice)
    return 'ok'


@app.route('/test/delete')
def testdelete():
    app.func.invoice_collection.delete_many({})
    return 'ok'


@app.route('/api/checkbtc/<addy>')
def apicheckbtc(addy: str):
    r = requests.get(f"https://bitcoinexplorer.org/api/address/{addy}").json()
    if "success" in r:
        if not r["success"]:
            return {"Success": False}, 200
    else:
        return {"Success": True}, 200


if __name__ == '__main__':
    app.func.connect_mongo(config["mongodb"])
    app.func.mongo_database("pfppay")
    app.func.mongo_collection("invoices")
    app.run(debug=True)
