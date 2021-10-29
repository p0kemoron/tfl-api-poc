# tfl-api-poc
A primitive python app built on top of TFL API to schedule requests. The app can be used to launch jobs to make calls to TFL Unified API.
These jobs can be instant or scheduled as per the requirement. 

## Usage
1. Clone github repository
2. Build using Dockerfile with the command: `docker build . -t flask-demo`
3. Run the container: `docker run -t -p 5555:8080 flask-demo`

The application should now be running on localhost at port 5555

## Parameters
The API accepts two parameters:

1. <b>schedule_time</b>:
   Optional. Represents the time at which the call to TFL API is to be made. If not passed, the job will be treated as an instant job.
   Must be in '%Y%m%dT%H:%M:%S' format if passed.
2. <b>lines</b>:
   Mandatory. Represents the lines for which information is required. Acceptable values are all line ids accepted by the Line API.

## API Calls
The following API calls are available as a part of this app:  

Method | URL | Parameter | Description
--- | --- | --- | ---
GET | http://localhost:5555/v1/tasks | - | Returns info on all tasks- past and scheduled
GET | http://localhost:5555/v1/tasks/<task_id> | - | Returns info for a particular task_id 
POST | http://localhost:5555/v1/tasks | schedule_time:optional  lines:mandatory | Creates a new task for given schedule_time and lines and returns its info
PATCH | http://localhost:5555/v1/tasks/<task_id> | schedule_time:optional  lines:mandatory | Updates a future task with the new parameters supplied
DELETE | http://localhost:5555/v1/tasks/<task_id> | - | Deletes info for the given task_id

## Job Information
The GET calls return the following job information:

1. <b>task_id:</b> Unique task_id created for each job
2. <b>task_type:</b> 'instant' or 'scheduled'
3. <b>request_time:</b> The time when job was created
4. <b>schedule_time:</b> The time when the call to TFL API is made
5. <b>lines:</b> Lines for which the information was requested for 
6. <b>task_status:</b> 'scheduled' if the call to TFL API hasn't been made yet. Else, 'success' on a successful call and 'fail' if the call failed
7. <b>tfl_resp:</b> JSON response from the TFL API


## Limitations

1. The 'scheduled_jobs' can not be converted into 'instant' jobs. A new job would need to be created with the same 'lines' parameter.
2. The scheduler uses an in-memory storage and hence the jobs will not be triggered if the app restarts.
3. The app assummes a single pre-authenticated user will be making the calls i.e. doesn't support functionality to support multiple users.
4. While effort has been made to use parameterized queries while using user-input, the app may still be prone to SQL injection attacks as input sanitization isn't included.
5. The database is passed into the Docker container instead of initializing a new one. This may be a cause of concern as the DB may be modified while testing etc.


## Developer's notes
I ended up spending 5-6 hours over the course of past two days to complete this task. This is because I wasn't familiar with the apscheduler library and ended up spending some time to go through the documentation to understand its working.  
In the past, I've relied either on abstractions like Airflow or bare cronjobs for my scheduling needs. This was a fun PoC to build and I got to learn a bit about apscheduler along the way.