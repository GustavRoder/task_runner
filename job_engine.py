from datetime import datetime

import json
import multiprocessing as mp
import os
import shutil
import time
import uuid






s_concurrent_job_cnt = 5
s_jobs_folder = '/tmp/job-engine/'






class JobEngine:







    def __init__(self):

        if os.path.exists(s_jobs_folder)==False:
            os.mkdir(s_jobs_folder)
        





    @staticmethod
    def check_jobs():

        jobs = JobEngine.list_jobs()
        running_jobs = [j for j in jobs if j['status']=='running']
        
        if len(running_jobs)<s_concurrent_job_cnt:

            jobs_not_started = [j for j in jobs if j['status']=='not-started']

            jobs_2_run = min(s_concurrent_job_cnt-len(running_jobs), len(jobs_not_started))
            for i in range(jobs_2_run):
                JobEngine.start_job(jobs_not_started[i]['job_id'])
            






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
        data = json.loads(file_content)

        return data







    @staticmethod
    def add_job(data):

        job_id = JobEngine.create_job_id()
        os.mkdir(os.path.join(s_jobs_folder,job_id))

        data["job_id"] = job_id
        data["status"] = "not-started"
        data["dt_added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        JobEngine.write_job_data_file(job_id, data)

        JobEngine.check_jobs()

        return job_id







    @staticmethod
    def remove_job(job_id):

        shutil.rmtree(os.path.join(s_jobs_folder,job_id))







    @staticmethod
    def start_job(job_id):
        
        if os.path.exists(os.path.join(s_jobs_folder,job_id))==False:
            raise Exception(f"A job with id='{job_id}' does not exist!")
        
        job_data = JobEngine.read_job_data_file(job_id)
        
        # Check for concurrent runnnig jobs

        jobs = JobEngine.list_jobs()
        running_jobs = [j for j in jobs if j['status']=='running']
        if len(running_jobs)>=s_concurrent_job_cnt:
            raise Exception('ERROR: The number of concurrent running jobs has reached its maximum!')
        
        # Start job

        print(f'Starting job_id={job_data["job_id"]}!')

        job_data["status"] = "running"
        JobEngine.write_job_data_file(job_id, job_data)

        # Start the job

        p = mp.Process(target=JobEngine.do_work, args=[job_data])
        
        p.start()
        # p.join()
        






    @staticmethod
    def do_work(job_data):

        print('----------------------------------------------')
        print(job_data)
        print('Executing CMD:')

        print("sleep......")
        time.sleep(5)
        print("done sleeping!")

        exit_code = os.system('ls')
        
        print('----------------------------------------------')

        print(exit_code)

        # Register finished
        job_data["status"] = "finished"
        JobEngine.write_job_data_file(job_data['job_id'], job_data)

        JobEngine.check_jobs()

        return f'done: {exit_code}'







    @staticmethod
    def list_jobs():

        jobs = []

        for job_id in os.listdir(os.path.join(s_jobs_folder)):
            if os.path.isdir(os.path.join(s_jobs_folder,job_id)):
                jobs.append(JobEngine.read_job_data_file(job_id))

        for job in jobs:
            job["dt_added"] = datetime.strptime(job["dt_added"],"%Y-%m-%d %H:%M:%S.%f")

        jobs = sorted(jobs, key=lambda x: x["dt_added"])

        return jobs






    