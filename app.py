from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import time
import threading
import random


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coffee.db"
db = SQLAlchemy(app)

class Coffee(db.Model):
    orderId = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(50))
    available = db.Column(db.Boolean)

with app.app_context():
    db.create_all()

def countdown(orderId, t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f"Order {orderId}: {timer}", end="\r")
        time.sleep(1)
        t -= 1

    try:    
        with app.app_context():
        # Mark the order as available after the countdown
            # order = db.session.execute(db.select(Coffee).filter_by(orderId=orderId)).scalars().first()
            order = Coffee.query.filter_by(orderId=orderId).first()
            # print(order)
            if order is not None:
                    order.available = True
                    db.session.commit()
            # db.session.execute(update(Coffee).where(orderId==orderId).values(available=True))
            # db.session.commit()
        print(f"Order {orderId} is now available!")
    except Exception as e:
                print(e)

# Store timers for active orders
timers = {}
options = ['Latte', 'Capuccino', 'Macchiato', 'Frepe', 'Mocha']

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/orders", methods=['POST', 'GET'])
def orders():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'confirm':
            itemName = request.form['coffee']
        else:
             itemName = random.choice(options)
        new_order = Coffee(itemName=itemName, available=False)

        # Add to db
        db.session.add(new_order)
        db.session.commit()

        # Get the new order ID
        new_orderId = new_order.orderId
        
        # Add that orderId to the timers dictionary with a countdown
        timers[new_orderId] = 30
        
        # Start a countdown thread for this order
        threading.Thread(target=countdown, args=(new_orderId, timers[new_orderId])).start()
        print(f"Started countdown for order {new_orderId}")

        return redirect(url_for('collect'))

    return render_template("orders.html", options=options)

@app.route("/collect", methods=['POST', 'GET'])
def collect():
    if request.method == 'POST':
        completedItem = int(request.form.get('collect-button'))
        db.session.execute(db.delete(Coffee).where(Coffee.orderId == completedItem))
        db.session.commit()

    orders = db.session.execute(db.select(Coffee).order_by(Coffee.orderId)).scalars()
    return render_template("collect.html", orders=orders)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='localhost', port=8080)
