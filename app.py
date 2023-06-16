import json

# from flask import Flask, jsonify, request, abort, session
from models import Post, Session, engine, Base
from aiohttp import web
from sqlalchemy.exc import IntegrityError

# Flask
# app = Flask("app")

# AIOHTTP
app = web.Application()


# Flask
# class HttpError(Exception):
#     def __init__(self, status_code: int, message: str | dict | list):
#         self.status_code = status_code
#         self.message = message
#
#
# @app.errorhandler(HttpError)
# def error_handler(er: HttpError):
#     response = jsonify({"status": "error", "message": er.message})
#     response.status_code = er.status_code
#     return response
#
#
# @app.route("/posts", methods=["GET", "POST"])
# def create():
#     if request.method == "GET":
#         posts = session.query(Post).all()
#         return jsonify([post.to_json() for post in posts])
#     if request.method == "POST":
#         if not request.json:
#             abort(400)
#         post = Post(
#             title=request.json.get('title'),
#             author=request.json.get('author'),
#             description=request.json.get('description')
#         )
#         session.add(post)
#         session.commit()
#         return jsonify(post.to_json()), 201
#
#
# @app.route("/posts/<int:id>", methods=["GET", "PATCH", "DELETE"])
# def detail_post(id):
#     if request.method == "GET":
#         post = session.query(Post).get(id)
#         if post is None:
#             abort(404)
#         return jsonify(
#             {
#                 "id": post.id,
#                 "title": post.title,
#                 "description": post.description,
#                 "author": post.author,
#                 "create_date": post.create_date.isoformat(),
#             }
#         )
#     if request.method == "PATCH":
#         post = session.query(Post).get(id)
#         print(request.json.get("author"))
#
#         post.title = request.json.get("title", post.title)
#         post.author = request.json.get("author", post.author)
#         post.description = request.json.get("description", post.description)
#         session.commit()
#         return jsonify(
#             {
#                 "id": post.id,
#                 "title": post.title,
#                 "description": post.description,
#                 "author": post.author,
#                 "create_date": post.create_date.isoformat(),
#             }
#         )
#     if request.method == "DELETE":
#         post = session.query(Post).get(id)
#         if post:
#             session.delete(post)
#             session.commit()
#         return jsonify(), 204

# AIOHTTP
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request["session"] = session
        response = await handler(request)
        return response


async def get_post(post_id: int, session: Session):
    post = await session.get(Post, post_id)
    if post is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "post not found"}),
            content_type="application/json",
        )
    return post


class PostView(web.View):
    @property
    def session(self):
        return self.request["session"]

    @property
    def post_id(self):
        return int(self.request.match_info["post_id"])

    async def get(self):
        post = await get_post(self.post_id, self.session)

        return web.json_response(
            {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'author': post.author,
                'create_date': int(post.create_date.timestamp())
            }
        )

    async def post(self):
        json_data = await self.request.json()
        post = Post(**json_data)
        try:
            self.session.add(post)
            await self.session.commit()
        except IntegrityError as er:
            raise web.HTTPConflict(
                text=json.dumps({"error": "post already exists"}),
                content_type="application/json",
            )
        return web.json_response({"id": post.id})

    async def patch(self):
        json_data = await self.request.json()
        post = await get_post(self.post_id, self.session)
        for field, value in json_data.items():
            setattr(post, field, value)
        try:
            self.session.add(post)
            await self.session.commit()
        except IntegrityError as er:
            raise web.HTTPConflict(
                text=json.dumps({"error": "post already exists"}),
                content_type="application/json",
            )
        return web.json_response({"id": post.id})

    async def delete(self):
        post = await get_post(self.post_id, self.session)
        await self.session.delete(post)
        await self.session.commit()
        return web.json_response({"id": post.id})


async def orm_context(app: web.Application):
    print("START")
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
    yield
    print("SHUT DOWN")
    await engine.dispose()


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)
app.add_routes(
    [
        web.post("/posts/", PostView),
        web.get("/posts/{post_id:\d+}", PostView),
        web.patch("/posts/{post_id:\d+}", PostView),
        web.delete("/posts/{post_id:\d+}", PostView),
    ]
)

if __name__ == "__main__":
    # Flask
    # app.run()

    # AIOHTTP
    web.run_app(app)
