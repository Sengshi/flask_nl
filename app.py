from flask import Flask, jsonify, request, abort, session
from models import Post, session

app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "message": er.message})
    response.status_code = er.status_code
    return response


@app.route("/posts", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        posts = session.query(Post).all()
        return jsonify([post.to_json() for post in posts])
    if request.method == "POST":
        if not request.json:
            abort(400)
        post = Post(
            title=request.json.get('title'),
            author=request.json.get('author'),
            description=request.json.get('description')
        )
        session.add(post)
        session.commit()
        return jsonify(post.to_json()), 201


@app.route("/posts/<int:id>", methods=["GET", "PATCH", "DELETE"])
def detail_post(id):
    if request.method == "GET":
        post = session.query(Post).get(id)
        if post is None:
            abort(404)
        return jsonify(
            {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "author": post.author,
                "create_date": post.create_date.isoformat(),
            }
        )
    if request.method == "PATCH":
        post = session.query(Post).get(id)
        print(request.json.get("author"))

        post.title = request.json.get("title", post.title)
        post.author = request.json.get("author", post.author)
        post.description = request.json.get("description", post.description)
        session.commit()
        return jsonify(
            {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "author": post.author,
                "create_date": post.create_date.isoformat(),
            }
        )
    if request.method == "DELETE":
        post = session.query(Post).get(id)
        if post:
            session.delete(post)
            session.commit()
        return jsonify(), 204


if __name__ == "__main__":
    app.run()
