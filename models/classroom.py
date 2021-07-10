from models.database import db

def create_class_code():
    from string import ascii_letters
    from random import choice
    code = ""
    while True:
        code = ""
        for letter in range(5):
            code = code + choice(ascii_letters)
        if Classroom.query.filter_by(code=code).first() is None:
            break

    return code

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(5), nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))

    def __init__(self, name, description, teacher) -> None:
        super().__init__()

        self.name = name
        self.description = description
        self.code = create_class_code()
        self.teacher = teacher

