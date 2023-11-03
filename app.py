from flask import *
import func
from flask import request

app = Flask(__name__)
app.func = func.processor()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/pay')
def custompay():
    addy = app.func.create_invoice(request.args.get('amount', default = 1, type = float), request.args.get('address', default = " ", type = str))
    return render_template("payment.html", image_url=addy)



if __name__ == '__main__':
    app.run(debug=True)
