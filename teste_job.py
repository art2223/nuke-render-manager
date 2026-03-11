# teste_queue.py
from job import Job
from queue_manager import QueueManager

qm = QueueManager()

# Criando 3 jobs
job1 = Job("C:/cena1.nk", [], "1001-1050")
job2 = Job("C:/cena2.nk", ["Write1"])
job3 = Job("C:/cena3.nk", ["Write_EXR", "Write_DPX"], "1001-1100")

qm.add_job(job1)
qm.add_job(job2)
qm.add_job(job3)

print("Fila inicial:")
for j in qm.jobs:
    print(f"  {j.nk_path} | writes: {j.writes}")

# Subindo o job3 para o topo
qm.move_up(job3.id)
qm.move_up(job3.id)

print("\nApós subir job3:")
for j in qm.jobs:
    print(f"  {j.nk_path} | writes: {j.writes}")

print(f"\nPróximo a renderizar: {qm.get_next_job().nk_path}")

# Removendo job2
qm.remove_job(job2.id)
print(f"\nApós remover job2, fila tem {len(qm.jobs)} jobs")

print("\nFeche e rode novamente — os jobs devem reaparecer (persistência)")