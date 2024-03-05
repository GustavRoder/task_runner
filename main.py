from flask import Flask
from job_engine import JobEngine




app = Flask(__name__)
JobEngine.init()




@app.route("/")
def list_jobs():
    
    jobs = JobEngine.list_jobs()

    html = "<html><body><table>"
    
    headers = ['job_id','status','job_type']
    
    html += "<thead><tr>"
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead>"
    
    html += "<tbody>"

    for job in jobs:
        html += "<tr>"
        html += f"<td>{job['job_id']}</td>"
        html += f"<td>{job['status']}</td>"
        html += f"<td>{job['job_type']}</td>"
        html += "</tr>"

    html += "</tbody></table></body></html>"

    return html








@app.route("/api/jobs/add")
def api_jobs_add():

    data = {
        "job_type": "cmd",
        "cmd": "ll /tmp",
    }

    return JobEngine.add_job(data)




if __name__ == "__main__":
    app.run(host='0.0.0.0')


