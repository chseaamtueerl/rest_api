from flask import Flask
import requests
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class PostModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(200), nullable = False)
	body = db.Column(db.String(50), nullable=False)

	def __repr__(self):
		return f"Post(userId = {userId}, title = {title}, body = {body})"

#db.create_all() - just for creating db at the beginning

post_put_args = reqparse.RequestParser()
post_put_args.add_argument("userId", type=int, help="ID pouzivatela", required=True)
post_put_args.add_argument("title", type=str, help="Titulok", required=True)
post_put_args.add_argument("body", type=str, help="Telo prispevku", required=True)

post_patch_args = reqparse.RequestParser()
post_patch_args.add_argument("title", type=str, help="Titulok")
post_patch_args.add_argument("body", type=str, help="Telo prispevku")

BASE = "http://127.0.0.1:5000/"

resource_fields = {
	'id': fields.Integer,
	'userId': fields.Integer,
	'title': fields.String,
	'body': fields.String
}

class Prispevok(Resource):
	@marshal_with(resource_fields)
	def put(self, post_id):
		args = post_put_args.parse_args()
		result = PostModel.query.filter_by(id=post_id).first()
		if result:
			abort(409, message="Prispevok s tymto ID uz existuje...")

		post = PostModel(id=post_id, userId=args['userId'], title=args['title'], body=args['body'])

		db.session.add(post)
		db.session.commit()

		return post, 201 # posted successfully

	@marshal_with(resource_fields)
	def get(self, post_id):
		result = PostModel.query.filter_by(id=post_id).first()
		if not result:
			#result = requests.get("https://jsonplaceholder.typicode.com/posts/" + str(post_id))
			if not result:
				abort(404, message="Prispevok nenajdeny...")
			# else:
			# 	result = requests.put(BASE + 'posts/' + str(post_id), result)
			
		return result

	@marshal_with(resource_fields)
	def patch(self, post_id):
		args = post_patch_args.parse_args()
		result = PostModel.query.filter_by(id=post_id).first()
		if not result:
			abort(404, message="Prispevok neexistuje...")

		if args['title']:
			result.title = args['title']
		if args['body']:
			result.body = args['body']

		db.session.commit()

		return result

	def delete(self, post_id): #finish/todo
		result = PostModel.query.filter_by(id=post_id).first()
		if not result:
			abort(404, message="Prispevok neexistuje...")

		db.session.delete(result)
		db.session.commit()
		
		return '', 204 # DELETED SUCCESSFULY

api.add_resource(Prispevok, "/posts/<int:post_id>")

if __name__ == "__main__":
	app.run(debug=True)
