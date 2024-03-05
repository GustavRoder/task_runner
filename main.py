from flask import Flask
from job_engine import JobEngine




app = Flask(__name__)
JobEngine.init()




@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"




@app.route("/api-list2")
def api_list():
    return "API"




@app.route("/api/jobs/add")
def api_jobs_add():

    return JobEngine.add_job()




if __name__ == "__main__":
    app.run(host='0.0.0.0')


