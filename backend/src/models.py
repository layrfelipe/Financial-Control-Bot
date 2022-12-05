from src import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    description = db.Column(db.Text)
    value = db.Column(db.Float)
    date = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}