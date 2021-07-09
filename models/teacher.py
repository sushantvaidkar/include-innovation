from models.database import db

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(10), nullable=False)

    name = db.Column(db.String(40), nullable=False)

    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __init__(self, name, email, password) -> None:
        super().__init__()
        self.user_type = "teacher"

        self.name = name
        self.email = email
        self.password = password
