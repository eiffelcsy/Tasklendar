from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
import re

# Initialize Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///task.db"
db = SQLAlchemy(app)

# Create database model
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(tz=timezone(timedelta(hours=8))))
    start = db.Column(db.DateTime, default=datetime.now())
    duration = db.Column(db.Float, default=0)
    end = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self) -> str:
        return "<Task %r>" % self.task_id
    
# Application route handling
# Homepage/List of All Tasks
@app.route("/", methods=["POST", "GET"])
def home():
        tasks = db.session.execute(db.select(Task).order_by(Task.timestamp)).scalars().all()
        return render_template("list.html", tasks=tasks)
    
# Add Tasks page
@app.route("/add/", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["task_name"]
        stime = datetime.strptime(request.form["start_time"], '%Y-%m-%dT%H:%M')
        etime = datetime.strptime(request.form["end_time"], '%Y-%m-%dT%H:%M')
        durat = etime - stime
        new_task = Task(
            task_name=name,
            start=stime,
            end=etime,
            duration= (durat / timedelta(minutes=1))
            )

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an error adding the task."
    else:
        return render_template("add.html")
    
# Delete Tasks page
@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = db.get_or_404(Task, id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting the task."

# Edit Tasks page
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def update(id):
    task = db.get_or_404(Task, id)
    if request.method == "POST":
        task.task_name = request.form["task_name"]
        task.start = datetime.strptime(request.form["start_time"], '%Y-%m-%dT%H:%M')
        task.end = datetime.strptime(request.form["end_time"], '%Y-%m-%dT%H:%M')
        task.duration = ((task.end - task.start) / timedelta(minutes=1))

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "There was a problem editing the task."
    else:
        return render_template("edit.html", task=task, isEdit=True)

@app.route("/today/")
def today():
    hours = [f"{hour:02d}{minute:02d}" for hour in range(24) for minute in [0, 30]]
    today = datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    hours_datetime = [datetime.strptime(today + hour, "%Y-%m-%d%H%M") for hour in hours]
    hours_dict = {}
    tasks_dict = {}

    today_tasks = db.session.execute(db.select(Task).where(Task.start.contains(today))).scalars().all()
    for task in today_tasks:
        tasks_dict[task.start] = {"task_name": task.task_name, "end_time": task.end, "duration": task.duration}

    for hourdt, hour in zip(hours_datetime, hours):
        hours_dict[hourdt] = hour

    return render_template("today.html", hours_dict=hours_dict, tasks_dict=tasks_dict)

if __name__ == "__main__":
    app.run(debug=True)