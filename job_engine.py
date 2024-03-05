from datetime import datetime

import json
import os
import uuid





s_jobs_folder = '/tmp/job-engine/'






class JobEngine:




    @staticmethod
    def init():

        if os.path.exists(s_jobs_folder)==False:
            os.mkdir(s_jobs_folder)





    @staticmethod
    def create_job_id():

        job_id = str(uuid.uuid1())[:8]
        return job_id





    @staticmethod
    def write_job_data_file(job_id, data):

        file_content = json.dumps(data, indent=2)

        job_data_file = open(os.path.join(s_jobs_folder,job_id,'_job.data'),'w')
        job_data_file.write(file_content)
        job_data_file.close()





    @staticmethod
    def read_job_data_file(job_id):

        job_data_file = open(os.path.join(s_jobs_folder,job_id,'_job.data'),'r')
        
        file_content = ''.join(job_data_file.readlines())
        print(file_content)
        data = json.loads(file_content)
        # data = {}
        return data







    @staticmethod
    def add_job(data):

        job_id = JobEngine.create_job_id()
        os.mkdir(os.path.join(s_jobs_folder,job_id))

        data["job_id"] = job_id
        data["status"] = "not-started"
        data["dt_added"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

        JobEngine.write_job_data_file(job_id, data)

        return job_id





    @staticmethod
    def start_job(job_id):
        
        if os.path.exists(os.path.join(s_jobs_folder,job_id))==False:
            raise Exception(f"A job with id='{job_id}' does not exist!")
        





    @staticmethod
    def list_jobs():

        jobs = []

        for job_id in os.listdir(os.path.join(s_jobs_folder)):
            if os.path.isdir(os.path.join(s_jobs_folder,job_id)):
                jobs.append(JobEngine.read_job_data_file(job_id))

        return jobs






    