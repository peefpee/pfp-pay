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
    data = json.loads(
        dumps(list(app.func.find_mongo({"invoice_id": request.args.get('id', default="0", type=int)})), indent=2))[0]
    return render_template("payment.html", image_url=app.func.create_qrcode(data["amount"], data["address"]),
                           invoiceid=request.args.get('id', default="0", type=int), amount=data["amount"],
                           address=data["address"])


if __name__ == '__main__':
    app.func.connect_mongo(config["mongodb"])
    app.func.mongo_database("pfppay")
    app.func.mongo_collection("invoices")
    app.run(debug=True)
