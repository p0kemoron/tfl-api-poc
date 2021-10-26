CREATE TABLE IF NOT EXISTS TASKS (
    task_id TEXT PRIMARY KEY NOT NULL,
    task_type TEXT NOT NULL,
    request_time TEXT NOT NULL,
    schedule_time TEXT NULL,
    lines TEXT NULL,
    task_status TEXT NOT NULL,
    tfl_resp TEXT NULL
)