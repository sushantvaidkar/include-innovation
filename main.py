from flask import Flask
from flask import render_template

# Database and Models
from models.database import db

app = Flask(__name__)
app.secret_key = "WCEHACKATHON"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)