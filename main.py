from flask import Flask, redirect
from job_engine import JobEngine




je = JobEngine()


app = Flask(__name__)




@app.route("/")
def list_jobs():
    
    jobs = JobEngine.list_jobs()

    html = "<html><body><table>"
    
    headers = ['job_id','dt_added','status','job_type','ctrl.start','ctrl.remove']
    
    html += "<thead><tr>"
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead>"
    
    html += "<tbody>"

    for job in jobs:
        html += "<tr>"
        
        html += f"<td>{job['job_id']}</td>"
        html += f"<td>{job['dt_added']}</td>"
        html += f"<td>{job['status']}</td>"
        html += f"<td>{job['job_type']}</td>"
        
        html += f"<td>"
        html += "<a href='/api/jobs/start/" + job['job_id'] + "'>START</a>" if job['status']=='not-started' else ""
        html += "</td>"
        html += "<td>"

        html += "<a href='/api/jobs/remove/" + job['job_id'] + "'>REMOVE</a>"
        html += "</td>"

        
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






@app.route("/api/jobs/start/<job_id>")
def api_jobs_start(job_id):

    JobEngine.start_job(job_id)

    print(f"Started {job_id}!")
    return redirect("/")






@app.route("/api/jobs/remove/<job_id>")
def api_jobs_remove(job_id):

    JobEngine.remove_job(job_id)

    print(f"Removed {job_id}!")
    return redirect("/")






if __name__ == "__main__":
    app.run(host='0.0.0.0')







