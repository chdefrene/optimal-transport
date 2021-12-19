from flask import Flask, Response

app = Flask(__name__)


@app.route('/')
def home():
    return 'Home Page Route'


@app.route("/api/route")
def calculate_route():
    pass



if __name__ == "__main__":
    app.run()
