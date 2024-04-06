from datetime import datetime

import json
import multiprocessing as mp
import os
import shutil
import uuid






s_concurrent_job_cnt = 1

s_jobs_folder = '/tmp/job-engine/'
s_jobs_dir = os.path.join(s_jobs_folder,'_jobs')
s_data_dir = os.path.join(s_jobs_folder,'_data')
s_batches_dir = os.path.join(s_data_dir,'batches')











class JobEngine:







    @staticmethod
    def init():

        # Main dir
        if os.path.exists(s_jobs_folder)==False:
            os.mkdir(s_jobs_folder)

        # Jobs dir
        if os.path.exists(s_jobs_dir)==False:
            os.mkdir(s_jobs_dir)
        
        # Data dir
        if os.path.exists(s_data_dir)==False:
            os.mkdir(s_data_dir)

        # Data -> Batches
        if os.path.exists(s_batches_dir)==False:
            os.mkdir(s_batches_dir)








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
    def get_batches():

        batches = []

        for fn in os.listdir(s_batches_dir):
            if fn.endswith('.b'):
                with open(os.path.join(s_batches_dir,fn), 'r') as f:
                    batch = json.loads(f.read())
                    batches.append(batch)

        return batches







    @staticmethod
    def create_new_batch_id(original_batch_id):
        
        batch_id = str(uuid.uuid1())[:8]
        with open (os.path.join(s_batches_dir,f'{batch_id}.b'), 'w', encoding='utf-8') as f:
            j = {'batch_id':batch_id,'original_batch_id':original_batch_id}
            json.dump(j, f, ensure_ascii=False, indent=2)

        return batch_id







    @staticmethod
    def create_batch_id(original_batch_id='not-given'):

        batch_id = None

        if original_batch_id=='not-given':
            batch_id = JobEngine.create_new_batch_id(original_batch_id)

        else:
            batches = JobEngine.get_batches()
            for batch in batches:
                if batch['original_batch_id']==original_batch_id:
                    batch_id = batch['batch_id']
            if batch_id is None:
                 batch_id = JobEngine.create_new_batch_id(original_batch_id)

        return batch_id








    @staticmethod
    def write_job_data_file(job_id, data):

        file_content = json.dumps(data, indent=2)

        job_data_file = open(JobEngine.get_job_file(job_id),'w')
        job_data_file.write(file_content)
        job_data_file.close()






    @staticmethod
    def get_job_dir(job_id):
        return os.path.join(s_jobs_dir,job_id)






    @staticmethod
    def get_job_file(job_id):
        return os.path.join(JobEngine.get_job_dir(job_id),'_job.data')






    @staticmethod
    def read_job_data_file(job_id):

        job_data_file = open(JobEngine.get_job_file(job_id),'r')
        
        file_content = ''.join(job_data_file.readlines())
        data = json.loads(file_content)

        return data







    @staticmethod
    def add_job(job):

        original_job_id = job['job_id'] if 'job_id' in job else 'not-given'
        original_batch_id = job['batch_id'] if 'batch_id' in job else 'not-given'

        job_id = JobEngine.create_job_id()
        job_dir = JobEngine.get_job_dir(job_id)

        batch_id = JobEngine.create_batch_id(original_batch_id)
        
        os.mkdir(job_dir)
        os.mkdir(os.path.join(job_dir,'data'))

        job["job_id"] = job_id
        job["original_job_id"] = original_job_id
        job["batch_id"] = batch_id
        job["original_batch_id"] = original_batch_id
        job["status"] = "not-started"
        job["dt_added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        JobEngine.write_job_data_file(job_id, job)

        JobEngine.check_jobs()

        return job








    @staticmethod
    def add_jobs(jobs):

        jobs_added = []

        for job in jobs:
            jobs_added.append(JobEngine.add_job(job))

        return jobs_added







    @staticmethod
    def remove_job(job_id):

        shutil.rmtree(os.path.join(s_jobs_dir,job_id))







    @staticmethod
    def remove_all_jobs():

        for f in os.listdir(s_jobs_dir):
            p = os.path.join(s_jobs_dir,f)

            if os.path.isdir(p):
                shutil.rmtree(p)







    @staticmethod
    def start_job(job_id):
        
        if os.path.exists(JobEngine.get_job_dir(job_id))==False:
            raise Exception(f"A job with id='{job_id}' does not exist!")
        
        job_data = JobEngine.read_job_data_file(job_id)
        
        # Check for concurrent runnnig jobs

        jobs = JobEngine.list_jobs()
        running_jobs = [j for j in jobs if j['status'].startswith('running')]
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

        ret_val = None

        if job_data['job_type'] == 'cmd':
            ret_val = JobEngine.do_work_cmd(job_data)

        return ret_val







    @staticmethod
    def do_work_cmd(job_data):

        # Make data folder
        job_dir = JobEngine.get_job_dir(job_data['job_id'])
        data_dir = os.path.join(job_dir,'data')
        os.chdir(data_dir)

        # Execute command
        cmd = f'{job_data["cmd"]} > cmd_output.data'
        exit_code = os.system(cmd)

        # Register finished
        job_data["status"] = "finished"
        JobEngine.write_job_data_file(job_data['job_id'], job_data)

        # Check for new jobs
        JobEngine.check_jobs()

        return f'done: {exit_code}'








    @staticmethod
    def list_jobs():

        jobs = []

        for job_id in os.listdir(s_jobs_dir):
            if os.path.isdir(JobEngine.get_job_dir(job_id)):
                jobs.append(JobEngine.read_job_data_file(job_id))

        for job in jobs:
            job["dt_added"] = datetime.strptime(job["dt_added"],"%Y-%m-%d %H:%M:%S.%f")

        jobs = sorted(jobs, key=lambda x: x["dt_added"])

        return jobs










    