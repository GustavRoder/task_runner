from flask import Flask, redirect, render_template, request
from job_engine import JobEngine





app = Flask(__name__)

JobEngine.init()








@app.route("/")
def home():
   return api_jobs_list()








@app.route("/api/jobs/list")
def api_jobs_list():
    return render_template('index.html', jobs=JobEngine.list_jobs())







@app.route("/api/jobs/add-single", methods=['POST'])
def api_jobs_add_single():
    
    job = request.json
    return JobEngine.add_job(job)








@app.route("/api/jobs/add-multiple", methods=['POST'])
def api_jobs_add_multiple():
    
    jobs = request.json
    return JobEngine.add_jobs(jobs)








@app.route("/api/jobs/start/<job_id>")
def api_jobs_start(job_id):

    JobEngine.start_job(job_id)

    print(f"Started {job_id}!")
    return redirect("/")






@app.route("/api/jobs/remove/<job_id>")
def api_jobs_remove(job_id):

    if job_id=='all':
        JobEngine.remove_all_jobs()
        print("Removed all jobs!")
        
    else:
        JobEngine.remove_job(job_id)
        print(f"Removed {job_id}!")
    
    return redirect("/")






if __name__ == "__main__":
    app.run(host='0.0.0.0')







