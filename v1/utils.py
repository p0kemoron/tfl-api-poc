from datetime import datetime as dt
import hashlib
import sqlite3

from flask.globals import request

# Add constants
DBNAME = "../tfl.db"
TABLE_NAME = "tasks"
TABLE_COLS = [
    "task_id",
    "task_type",
    "request_time",
    "schedule_time",
    "lines",
    "task_status",
    "tfl_resp",
]
INPUT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_db():
    return sqlite3.connect(DBNAME)


def get_task_id():
    dt_str = dt.strftime(dt.now(), "%D %T %s")
    return str(hashlib.sha256(dt_str.encode("utf-8")).hexdigest())[-8:]


def get_tfl_resp(lines):
    req = request.get(f"https://api.tfl.gov.uk/Line/{lines}/Disruption")
    if req.status_code == 200:
        task_status = "success"
    else:
        task_status = "failure"
    return req.text, task_status


def get_tasks():
    tasks = []
    try:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * from {TABLE_NAME}")
        task_list = cur.fetchall()
        for item in task_list:
            task = {k: item[k] for k in item.keys()}
        tasks.append(task)
        resp, status = tasks, 200
    except:
        resp, status = [{"responseErrorText": "Couldn't fetch reqd info"}], 503
    return resp, status


def get_specific_task(task_id):
    tasks = []
    try:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * from {TABLE_NAME} WHERE task_id = ?", (task_id,))
        task_list = cur.fetchall()
        for item in task_list:
            task = {k: item[k] for k in item.keys()}
        tasks.append(tasks)
        if len(tasks) == 1:
            resp, status = task, 200
        else:
            resp, status = tasks, 200
    except:
        resp, status = [{"responseErrorText": "Couldn't find task info"}], 404
    return resp, status


def del_specific_task(task_id):
    try:
        conn = get_db()
        conn.execute(f"DELETE from {TABLE_NAME} where task_id = ?", (task_id,))
        conn.commit()
        resp, status = {"responseText": f"Task {task_id} deleted"}, 200
    except:
        conn.rollback()
        resp, status = {"responseErrorText": f"Couldn't delete task {task_id}"}, 503
    conn.close()
    return resp, status


def update_task(task_info):
    if "task_id" not in task_info.keys():
        return {"responseErrorText": f"Invalid input"}, 400
    query_suffix = "where task_id = ?"

    if any(["schedule_time", "lines"]) in task_info.keys():
        update_query = f"UPDATE {TABLE_NAME} set "
        if "schedule_time" in task_info.keys():
            schedule_time = task_info["schedule_time"]
            update_query += "schedule_time = ? " + query_suffix
            try:
                conn = get_db()
                conn.execute(update_query,(schedule_time,task_info["task_id"],))
                conn.commit()
            except:
                conn.rollback()
                return {"responseErrorText": f"Couldn't update task {task_info}"}, 503
        if "lines" in task_info.keys():
            lines = task_info["lines"]
            update_query += "lines = ? " + query_suffix
            try:
                conn = get_db()
                conn.execute(update_query,(schedule_time,task_info["task_id"],))
                conn.commit()
            except:
                conn.rollback()
                return {"responseErrorText": f"Couldn't update task {task_info}"}, 503
        conn.close()
        return get_specific_task(task_info["task_id"])


def create_new_task(req_info):
    # Default task parameters
    task_id = get_task_id()
    task_type = "instant"
    request_time = dt.now().strftime(INPUT_DATE_FORMAT)
    task_status = "scheduled"
    schedule_time = None
    tfl_resp = None

    if "lines" not in req_info.keys():
        return {"responseErrorText": f"Invalid input"}, 400
    lines = req_info["lines"]

    if "schedule_time" in req_info.keys():
        schedule_time = req_info["schedule_time"]
        try:
            schd_stmp = dt.strptime("2021-10-26T11:24:02", INPUT_DATE_FORMAT)
        except:
            return {"responseErrorText": f"Invalid input"}, 400

        task_type = "scheduled"

    # Fetch TFL data
    tfl_resp, task_status = get_tfl_resp(lines)

    insert_query = f"""INSERT INTO {TABLE_NAME} VALUES \
        ({task_id}, {task_type}, {request_time}, ?, ?, {task_status}, {tfl_resp})
        """
    try:
        conn = get_db()
        conn.execute(insert_query,(schedule_time,lines,))
        conn.commit()
        resp, status = {"responseText": f"Task {task_id} created"}, 200
    except:
        conn.rollback()
        resp, status = {"responseErrorText": f"Couldn't delete task {task_id}"}, 503
    conn.close()
    return resp, status
