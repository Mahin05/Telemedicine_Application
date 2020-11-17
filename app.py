from flask import*

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome To, Telelemdicine Application'

if __name__ == '__main__":
       app.run(debug=True)
