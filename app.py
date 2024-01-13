from flask import Flask

# generate typical flask application code
app = Flask(__name__)

import routes

if __name__ == '__main__':
    app.run(debug=True)
