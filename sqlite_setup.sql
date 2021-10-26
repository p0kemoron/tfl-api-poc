CREATE TABLE IF NOT EXISTS TASKS (
    task_id TEXT PRIMARY KEY NOT NULL,
    task_type TEXT NOT NULL,
    request_time TEXT NOT NULL,
    schedule_time TEXT NULL,
    lines TEXT NULL,
    task_status TEXT NOT NULL,
    tfl_resp TEXT NULL
);

INSERT INTO TASKS VALUES
    (1,'demo','2021',NULL,'central','demo','resp_1'),
    (2,'demo','2021',NULL,'central','demo','resp_2'),
    (3,'demo','2021',NULL,'central','demo','resp_3');