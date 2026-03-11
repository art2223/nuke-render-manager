# teste_runner.py
import runner
from job import Job
from queue_manager import QueueManager

qm = QueueManager()
qm.jobs = []

job1 = Job("C:/cena1.nk", [], "1001-1050")
job2 = Job("C:/cena2.nk", ["Write1", "Write_EXR"])
job3 = Job("C:/cena3.nk", ["Write_DPX"])

qm.add_job(job1)
qm.add_job(job2)
qm.add_job(job3)

# Apenas testa a montagem dos comandos, sem executar nada
for job in qm.jobs:
    writes_to_run = job.writes if job.writes else [None]
    for write in writes_to_run:
        if write is None:
            cmd = [runner.NUKE_EXE, "-i", "-x", job.nk_path]
        else:
            cmd = [runner.NUKE_EXE, "-i", "-X", write, job.nk_path]
        if job.frame_range:
            cmd.append(job.frame_range)
        print(f"Comando que seria executado: {' '.join(cmd)}")