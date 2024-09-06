from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = "Satwik"
    return render_template("hello.html", name=name)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
