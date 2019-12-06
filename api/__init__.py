import os
import random
import requests

from flask import Flask, request, jsonify

# from flask_cors import CORS
from flask_restful import Api, Resource

# from sqlalchemy import exc

# from models import setup_db, Question, Category

# QUESTIONS_PER_PAGE = 10

hatchways_api_url = "https://hatchways.io/api/assessment/blog/posts?tag=tech"
route_1 = "/api/ping"
route_2 = "/api/posts"


# def paginate(request, selection):
#     page = request.args.get('page', 1, int)
#     start = (page - 1) * QUESTIONS_PER_PAGE
#     end = start + QUESTIONS_PER_PAGE
#     return [question.format() for question in selection[start:end]]


# Application factory
def create_app(test_config=None):
    app = Flask(__name__)

    # Initializes Cross Origin Resource sharing for the app
    # CORS(app)
    # # Set Access-Control-Allow
    # @app.after_request
    # def after_request(response):
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    #     return response

    # if not test_config:
    #     setup_db(app, os.getenv('DEV_DB_URI'))
    # else:
    #     setup_db(app, os.getenv('TEST_DB_URI'))

    api = Api(app)

    class Ping(Resource):
        def get(self):
            return {"success": True}, 200

    class Blog(Resource):
        def get(self):

            # Error messages
            tag_error_responses = {"error": "Tags parameter is required"}
            sort_by_error_responses = {"error": "sortBy parameter is invalid"}
            direction_error_responses = {"error": "direction parameter is invalid"}
            unclear_error_responses = {
                "error": "Possible Network/Internet connection error."
            }

            # Parse URL arguments/parameters
            tags_string = request.args.get("tags", None, str)
            if tags_string is None:
                return tag_error_responses, 400

            sort_by = request.args.get("sortBy", "id")
            if sort_by not in ["id", "reads", "likes", "popularity"]:
                return sort_by_error_responses, 400

            direction = request.args.get("direction", "asc")
            if direction not in ["asc", "desc"]:
                return direction_error_responses, 400

            tags = tags_string.strip().lower().split(",")

            # Send HTTP GET request to gather data from provider
            try:
                posts = []
                for tag in tags:
                    resp = requests.get(
                        f"https://hatchways.io/api/assessment/blog/posts?tag={tag}"
                    ).json()
                    posts += resp["posts"]

                # Sort in-place based on desired (parameters) criteria
                is_reverse = True if direction == "desc" else False
                posts.sort(key=lambda x: x[sort_by], reverse=is_reverse)

                return {"posts": posts}, 200

            except:
                return unclear_error_responses, 400

    # Resources
    api.add_resource(Ping, route_1)
    api.add_resource(Blog, route_2)

    # Error handlers for expected errors including 404 and 422.
    @app.errorhandler(400)
    def bad_request(error):
        error_message = (
            "The server could not understand the request due to invalid syntax."
        )
        return jsonify({"success": False, "error": 400, "message": error_message}), 400

    @app.errorhandler(404)
    def requested_method_not_found(error):
        error_message = (
            "The server can not find requested resource. "
            "The endpoint may be valid but the resource itself does not exist."
        )
        return jsonify({"success": False, "error": 404, "message": error_message}), 404

    return app
