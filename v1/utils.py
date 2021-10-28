from datetime import timezone, datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
import hashlib
import sqlite3
import requests


# Add constants
DBNAME = "/app/tfl.db"
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

# Scheduler configuration
scheduler = BackgroundScheduler(timzone=timezone.utc)
scheduler.start()

def get_db():
    return sqlite3.connect(DBNAME)


def get_task_id():
    dt_str = dt.strftime(dt.now(), "%D %T %s")
    return str(hashlib.sha256(dt_str.encode("utf-8")).hexdigest())[-8:]


def get_tfl_resp(lines):
    req = requests.get(f"https://api.tfl.gov.uk/Line/{lines}/Disruption")
    if req.status_code == 200:
        task_status = "success"
    else:
        task_status = "failure"
    return req.text, task_status


def sch_tfl_resp(lines,task_id):
    tfl_resp, task_status = get_tfl_resp(lines)
    update_query = f"""UPDATE {TABLE_NAME} set task_status='{task_status}', \
        tfl_resp='{tfl_resp}' where task_id='{task_id}'"""
    conn=get_db()
    conn.execute(update_query)
    conn.commit()
    return None


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
        resp, status = [{"responseErrorText": "Couldn't fetch reqd info"}], 500
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
        resp, status = {"responseErrorText": f"Couldn't delete task {task_id}"}, 500
    conn.close()
    return resp, status


def update_task(schedule_time,lines,task_id):
    update_query = f"UPDATE {TABLE_NAME} set "
    query_suffix = " where task_id = ?"
    
    conn = get_db()    
    if schedule_time:
        sch_query = update_query + " schedule_time = ? " + query_suffix
        try:
            conn.execute(sch_query,(schedule_time,task_id,))
            conn.commit()
        except:
            conn.rollback()
            return {"responseErrorText": f"Couldn't update task {task_id}"}, 500
    if lines:
        line_query = update_query + " lines = ? " + query_suffix
        try:
            conn.execute(line_query,(lines,task_id,))
            conn.commit()
        except:
            conn.rollback()
            return {"responseErrorText": f"Couldn't update task {task_id}"}, 500
    conn.close()
    return get_specific_task(task_id)


def create_new_task(schedule_time, lines):
    # Default task parameters
    task_id = get_task_id()
    task_type = "instant"
    request_time = dt.now().strftime(INPUT_DATE_FORMAT)
    task_status = "scheduled"
    tfl_resp = None

    if lines is None:
        return {"responseErrorText": "Invalid input: lines can't be empty"}, 400

    if schedule_time:
        try:
            schd_stmp = dt.strptime(schedule_time, INPUT_DATE_FORMAT)
        except:
            return {"responseErrorText": "Invalid input: invalid date format"}, 400
        task_type = "scheduled"
        scheduler.add_job(sch_tfl_resp, trigger='date',
                        next_run_time=str(schd_stmp), args=[lines,task_id])
    else:
        # Fetch TFL data
        tfl_resp, task_status = get_tfl_resp(lines)

    insert_query = f"""INSERT INTO {TABLE_NAME} VALUES \
        ("{task_id}", "{task_type}", "{request_time}", ?, ?, "{task_status}", "{tfl_resp}") \
        """
    conn = get_db()
    try:
        conn.execute(insert_query,(schedule_time,lines,))
        conn.commit()
        resp, status = get_specific_task(task_id)
    except:
        conn.rollback()
        resp, status = {"responseErrorText": f"Couldn't create task {task_id}"}, 500
    conn.close()
    return resp, status
