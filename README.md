# Daysavvy - Daily Task Scheduler API
Python Flask API that schedules daily tasks based on priority.

## Endpoints
- POST /tasks - Add task (name, duration, priority)
- GET /tasks - List tasks
- GET /schedule - Get optimized schedule
- GET /analytics/daily - Daily analytics

## Run Locally
pip install -r requirements.txt
python app.py
