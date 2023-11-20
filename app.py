import json
from datetime import datetime
from bson.json_util import dumps
from flask import *
from flask import request
from flask_wtf.csrf import CSRFProtect, CSRFError

import func
import requests

config = json.load(open('config.json'))
app = Flask(__name__)
app.func = func.processor()
app.secret_key = config["secretkey"]
csrf = CSRFProtect(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.errorhandler(CSRFError)
def handle_csrf_error():
    return render_template('csrf.html'), 400


@app.route('/pay')
def pay():
    return render_template('pay.html')


@app.route('/payinvoice')
def payinvoice():
    return 'Go to /payinvoice/<invoiceid>', 301


@app.route('/pay/create', methods=["POST"])
def paycreate():
    addy = request.form.get('address', type=str)
    url = f"http://127.0.0.1:5000/{url_for('apicheckbtc', addy=addy)}"
    print(url)
    if not requests.get(url).json()["Success"]:
        return {"Success": "False", "Error": "Invalid Address"}, 401
    invoice = func.invoice(app.func.count_mongo(app.func.invoice_collection) + 1, addy,
                           request.form.get('amount', type=float), False)
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


@app.route('/payinvoice/check', methods=["POST"])
def payinvoiceidcheck():
    txid = request.form.get("txid")
    invoiceid = request.form.get("invoiceid")
    r = requests.get(f'{config["hosturl"]}/api/checkbtc/txid/{txid}').json()
    if r["Success"] == False:
        return r["Error"], 404
    a = datetime.timestamp(datetime.now())
    timestamp = r["Timestamp"]
    diff = int(a - timestamp)
    if diff > 6000:
        return {"Success": False, "Error": "Transaction id older than 100 mins"}, 402

    app.func.update_mongo({"invoice_id": int(invoiceid)})
    url = f"{config['hosturl']}/payinvoice/{invoiceid}"
    return redirect(url)


@app.route('/api/delete')
def apidelete():
    app.func.invoice_collection.delete_many({})
    return 'ok'


@app.route('/api/checkbtc/addy/<addy>')
def apicheckbtc(addy: str):
    r = requests.get(f"https://bitcoinexplorer.org/api/address/{addy}").json()
    if "success" in r:
        if not r["success"]:
            return {"Success": False}, 200
    else:
        return {"Success": True}, 200


@app.route('/api/checkbtc/txid/<txid>')
def apicheckbtctxid(txid: str):
    r = requests.get(f"https://bitcoinexplorer.org/api/tx/{txid}").json()
    if "error" in r:
        return {"Success": False, "Error": "Unkown txid"}, 200
    if "vout" not in r:
        return {"Success": False, "Error": "Unkown txid"}, 200
    if "time" not in r:
        return {"Success": False, "Error": "Transaction not confirmed, Please retry later"}, 200
    return {"Success": True, "Txid": txid, "Amount": r["vout"][0]["value"], "Timestamp": r["time"],
            "Output": r["vout"][0]["scriptPubKey"]["address"]}





if __name__ == '__main__':
    app.func.connect_mongo(config["mongodb"])
    app.func.mongo_database("pfppay")
    app.func.mongo_invoiceccollection("invoices")
    app.run(debug=True)
