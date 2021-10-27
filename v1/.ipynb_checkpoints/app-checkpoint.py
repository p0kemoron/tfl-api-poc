from flask import Flask, Response, jsonify, request
from flask.helpers import make_response
import requests
from .utils import *

app = Flask(__name__)


@app.route("/v1/tasks", methods=["GET", "POST"])
def api_tasks():
    if request.method == "GET":
        resp, status = get_tasks()
        return make_response(jsonify(resp), status)
    if request.method == "POST":
        schedule_time = request.form.get('schedule_time')
        lines = request.form.get('lines')
        resp, status = create_new_task(schedule_time,lines)
        return make_response(jsonify(resp), status)


@app.route("/v1/tasks/<task_id>", methods=["GET"])
def api_get_task(task_id):
    resp, status = get_specific_task(task_id)
    return make_response(jsonify(resp), status)


@app.route("/v1/tasks/<task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    resp, status = del_specific_task(task_id)
    return make_response(jsonify(resp), status)


@app.route("/v1/tasks/<task_id>", methods=["PATCH"])
def api_update_task():
    schedule_time = request.form.get('schedule_time')
    lines = request.form.get('lines')
    print(schedule_time)
    print(lines)
    
    resp, status = update_task(schedule_time,lines)
    return make_response(jsonify(resp), status)


@app.route("/heartbeat")
def health():
    return Response("OK", status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
