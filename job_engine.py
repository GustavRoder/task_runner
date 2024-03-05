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
    def add_job():

        job_id = JobEngine.create_job_id()
        os.mkdir(os.path.join(s_jobs_folder,job_id))
        
        return job_id




    