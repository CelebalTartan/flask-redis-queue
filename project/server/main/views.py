# project/server/main/views.py


import redis
from rq import Queue, Connection
from flask import Blueprint, jsonify, request, current_app

from project.server.main.tasks import create_task

main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/delay", methods=["POST"])
def run_task():
    sleep_time = request.form["sleep_time"]
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        delay = q.enqueue(create_task, sleep_time)
    response_object = {
        "status": "success",
        "data": {
            "delay_id": delay.get_id()
        }
    }
    return jsonify(response_object), 202


@main_blueprint.route("/delay/<delay_id>", methods=["GET"])
def get_status(delay_id):
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        delay = q.fetch_job(delay_id)
    if delay:
        response_object = {
            "status": "success",
            "data": {
                "delay_id": delay.get_id(),
                "delay_status": delay.get_status(),
                "delay_result": delay.result,
            "status_code": 200
            },
        }
    else:
        response_object = {"status": "error", "status_code": 404}
    return jsonify(response_object)
