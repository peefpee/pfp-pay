from flask import *
import func

app = Flask(__name__)
app.func = func.processor()


@app.route('/')
def index():
    addy = app.func.create_invoice(1.5, "3GQhVzLgLJgk6XTwir8BgiAVYXTGA3AYRLkArw1JhMY2")
    return render_template("payment.html", image_url=addy)


if __name__ == '__main__':
    app.run(debug=True)
