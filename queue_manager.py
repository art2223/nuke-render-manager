import json
import os
from job import Job

SAVE_FILE = "jobs.json"
DONE_FILE = "done.json"


class QueueManager:
    def __init__(self):
        self.jobs = []
        self.load()

        # OPERAÇÒES DA FILA # 

    def add_job(self, job):
        # Add job no final da fila #
        self.jobs.append(job)
        self.save()

    def remove_job(self, job_id):
        # Remove um job pelo seu ID #
        self.jobs = [j for j in self.jobs if j.id != job_id]
        self.save()

    def move_up(self, job_id):
        # Move um job para cima na fila #
        index = self._find_index(job_id)
        if index > 0:
            self.jobs[index], self.jobs[index - 1] = self.jobs[index - 1], self.jobs[index]
            self.save()

    def move_down(self, job_id):
        # Move um job para baixo na fila #
        index = self._find_index(job_id)
        if index < len(self.jobs) - 1: # Só move se nao for o ultimo
            self.jobs[index], self.jobs[index + 1] = self.jobs[index + 1], self.jobs[index]
            self.save()

    def get_next_job(self):
        # retorna o proximo job com status waiting sem remove-lo da lista #
        for job in self.jobs:
            if job.status == "waiting":
                return job
        return None
    


    # --- PERSISTENCIA --- #



    def save(self):
        # Salva a lista de jobs no JSON #
        data = [job.to_dict() for job in self.jobs]
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        # Carrega os jobs do JSON #
        if not os.path.exists(SAVE_FILE):
            return
        
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        self.jobs = [Job.from_dict(d) for d in data]

        for job in self.jobs:
            if job.status == "running":
                job.status = "waiting"



    # Utilitarios #


    def _find_index(self, job_id):
        # Econtra posicao do job na lista por ID #
        for i, job in enumerate(self.jobs):
            if job.id == job_id:
                return i
        return -1
    

    # Arquiva em done.json

    def archive_done_jobs(self):
        # Move jobs done para done.json e remove do jobs.json
        done_jobs = [j for j in self.jobs if j.status == "done"]
        active_jobs = [j for j in self.jobs if j.status!= "done"]


        if not done_jobs:
            return
        
        existing = []
        if os.path.exists(DONE_FILE):
            with open(DONE_FILE, "r") as f:
                existing = json.load(f)

        existing.extend([j.to_dict() for j in done_jobs])

        with open(DONE_FILE, "w") as f:
            json.dump(existing, f, indent=4)

        self.jobs = active_jobs
        self.save()