from bson.json_util import dumps
from flask import *
from flask import request
import func
import json

config = json.load(open('config.json'))
app = Flask(__name__)
app.func = func.processor()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/pay')
def custompay():
    addy, invoiceid = app.func.create_invoice(request.args.get('amount', default=1, type=float),
                                              request.args.get('address', default=" ", type=str))

    return render_template("payment.html", image_url=addy, invoiceid=invoiceid,
                           address=request.args.get('address', default=" ", type=str),
                           amount=request.args.get('amount', default=1, type=float))


@app.route('/payinvoice')
def payinvoice():
    return 'Go to /payinvoice/<id>',301
@app.route('/payinvoice/<invoiceid>')
def payinvoiceid(invoiceid):
    invoiceid = int(invoiceid)
    if invoiceid == 1:
        return "404", 404
    elif invoiceid >= app.func.count_mongo(app.func.invoice_collection):
        return "404", 404
    dataa = list(app.func.find_mongo({"invoice_id": invoiceid}))
    print(dataa)
    data = json.loads(dumps(dataa, indent=2))[0]
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
                           request.args.get('amount', type=int), False)
    app.func.add_invoice(invoice)
    return 'ok'


if __name__ == '__main__':
    app.func.connect_mongo(config["mongodb"])
    app.func.mongo_database("pfppay")
    app.func.mongo_collection("invoices")
    app.run(debug=True)
