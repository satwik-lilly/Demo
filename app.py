# creating a costa cafe webapp
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coffee.db"
db = SQLAlchemy(app)

class Coffee(db.Model):
    orderId = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(50))

# Ensure tables are created before running the app
with app.app_context():
    db.create_all()

# 3 routes - /home, /order, /collect
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/orders", methods=['POST', 'GET'])
def orders():
    itemName = None
    orders = []
    if request.method == 'POST':
        itemName = request.form['coffee']
        new_order = Coffee(itemName=itemName)
        db.session.add(new_order)
        db.session.commit()
        orders = db.session.execute(db.select(Coffee).order_by(Coffee.orderId)).scalars()
        return redirect(url_for('display'), 404)
    return render_template("orders.html", orders = orders)
    # return redirect(url_for("collect", orders=orders))

@app.route("/collect", methods=['POST', 'GET'])
def display():
# @app.route("/collect", methods=['POST'])
# def collect():
    completedItem = None
    print("collecting")
    try:
        if request.method == 'POST':
            completedItem = int(request.form.get('collect-button'))
            print(completedItem, "deleted")
            db.session.execute(db.delete(Coffee).where(Coffee.orderId == completedItem))
            # Coffee.query.filter_by(id=completedItem).delete()
            # Coffee.query.filter_by(Coffee.orderId==completedItem).delete()
            db.session.commit()
    except ValueError:
        return "Invalid order ID", 400
    except Exception as e:
            # Log or handle the exception
        return f"An error occurred: {str(e)}", 500
    
    orders = db.session.execute(db.select(Coffee).order_by(Coffee.orderId)).scalars()
    return render_template("collect.html", orders = orders)
    
    # return redirect(url_for('display'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.autoflush = False
    app.run(debug=True, host='localhost', port=8080)

