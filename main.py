from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import requests


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/VictorinaDB'
""" Вместо указанных даных поместить свои данные postgresql в таком виде
 'postgresql://<username>:<password>@<server>:5432/<db_name>' """
app.debug = True
db = SQLAlchemy(app)


class VictorinaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String)
    answer_text = db.Column(db.String)
    question_date = db.Column(db.String)

    def __repr__(self):
        return f"The question is {self.question_text}"


"""Создание базы данных. Перед первым запуском скрипта - раскомментировать.
 После первого запуска скрипта - закомментировать."""
# db.create_all()


resource_fields = {
    'id': fields.Integer,
    'question_text': fields.String,
    'answer_text': fields.String,
    'question_date': fields.String,
}


def if_exists(income_id, question_num, i):
    if VictorinaModel.query.filter_by(id=income_id).first() is not None:
        result = requests.get(f"https://jservice.io/api/random?count={question_num - i - 1}")
        json_res = result.json()
        question_num = json_res[i]['id']
        if_exists(income_id, question_num, i)


class Victorina(Resource):
    @marshal_with(resource_fields)
    def get(self, question_id: int):
        result = VictorinaModel.query.get(id=question_id)
        return result

    @marshal_with(resource_fields)
    def post(self, question_num):
        result = requests.get(f"https://jservice.io/api/random?count={question_num}")
        json_res = result.json()
        for i in range(question_num):
            if_exists(json_res[i]['id'], question_num, i)
            new_question = VictorinaModel(
                id=json_res[i]['id'],
                question_text=json_res[i]['question'],
                answer_text=json_res[i]['answer'],
                question_date=json_res[i]['created_at']
            )
            db.session.add(new_question)
            db.session.commit()
        return json_res

api.add_resource(Victorina, "/victorina/<int:question_num>")

if __name__ == '__main__':
    app.run(debug=True)