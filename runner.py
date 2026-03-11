import subprocess
import os
import sys
from queue_manager import QueueManager


NUKE_EXE = os.environ.get("NUKE_EXE")

def build_command(job):

    # Monta o comando para render com base nos dados do job.

    if job.writes:
        cmd = [NUKE_EXE, "-i", "-X", job.writes[0], job.nk_path]
    else:
        cmd = [NUKE_EXE, "-i", "-x", job.nk_path]

    if job.frame_range:
        cmd.append(job.frame_range)

    return cmd



def run_job(job, queue_manager, on_status_change=None, on_log=None):

    # Executa um unico job.
    # job: job que será executado
    # queue_manager: para atualizar e salvar o status
    # on_status_change: função opcional para atualizar status
    # on_log: função opcional chamada a cada linha de output do nuke


    def set_status(status):
        job.status = status
        queue_manager.save()
        if on_status_change:
            on_status_change(job)


    writes_to_run = job.writes if job.writes else [None]

    set_status("running")


    for write in writes_to_run:
        if write is None:
            cmd = [NUKE_EXE, "-i", "-x", job.nk_path]
        else:
            cmd = [NUKE_EXE, "-i", "-X", write, job.nk_path]

        if job.frame_range:
            cmd.append(job.frame_range)


        cmd_str = " ".join(cmd)
        print(f"Executando: {cmd_str}")
        if on_log:
            on_log(f">>> {cmd_str}")


        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW  # impede que suba uma janela de CMD
        )

        for line in process.stdout:
            line = line.strip()
            print(line)
            if on_log:
                on_log(line)

        process.wait()

        if process.returncode != 0:
            set_status("error")
            print(f"Erro no write '{write}' --- abortando job.")
            if on_log:
                on_log(f"[ERRO] Falhou no write '{write}'")
            return # Para de executar writes seguintes
        

    set_status("done")
    print(f"Job concluído: {job.nk_path}. Writes executados: {write}.")




def run_queue(queue_manager, on_status_change=None, on_log=None):
    # Roda os jobs waiting da fila, um por vez.

    while True:
        job = queue_manager.get_next_job()
        if job is None:
            if on_log:
                on_log("=== Fila concluída ===")
            break
        run_job(job, queue_manager, on_status_change, on_log)