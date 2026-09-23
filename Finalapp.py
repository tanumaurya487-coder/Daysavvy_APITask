from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daysavvy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model - DaySavvy ke hisab se
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # Work, Personal, Health, Learning, Finance
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(10), nullable=False) # High, Medium, Low
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

# Home Route - DaySavvy Branding ke liye
@app.route('/')
def home():
    return jsonify({
        "startup": "DaySavvy",
        "project": "DaySavvy Task Management API",
        "message": "API built specifically for DaySavvy startup",
        "endpoints": {
            "create_task": "POST /tasks",
            "get_tasks": "GET /tasks?status=pending&category=Work",
            "complete_task": "PUT /tasks/<id>/complete",
            "analytics": "GET /analytics/daily-summary"
        }
    })

# 1. POST /tasks - Naya Task Banana
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('priority'):
        return jsonify({"error": "title and priority are required"}), 400

    if data['priority'] not in ['High', 'Medium', 'Low']:
        return jsonify({"error": "priority must be High, Medium, or Low"}), 400

    allowed_categories = ['Work', 'Personal', 'Health', 'Learning', 'Finance']
    if data.get('category') and data.get('category') not in allowed_categories:
        return jsonify({"error": f"category must be one of {allowed_categories}"}), 400

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "due_date format must be YYYY-MM-DD"}), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        category=data.get('category'),
        due_date=due_date,
        priority=data['priority']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# 2. GET /tasks - Filter ke saath Tasks Dekhna
@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    category = request.args.get('category')
    
    query = Task.query
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

# 3. PUT /tasks/<id>/complete - Task Complete Karna
@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(task.to_dict()), 200

# 4. GET /analytics/daily-summary - DaySavvy ka Daily Report
@app.route('/analytics/daily-summary', methods=['GET'])
def daily_summary():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    total_created_today = Task.query.filter(Task.created_at >= today_start).count()
    total_tasks = Task.query.count()
    total_completed = Task.query.filter_by(status='completed').count()
    overdue_count = Task.query.filter(Task.due_date < today, Task.status != 'completed').count()

    completion_rate = round((total_completed / total_tasks * 100), 2) if total_tasks > 0 else 0

    return jsonify({
        "date": today.isoformat(),
        "for_startup": "DaySavvy",
        "total_tasks_created_today": total_created_today,
        "completion_rate_percent": completion_rate,
        "overdue_tasks_count": overdue_count
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
