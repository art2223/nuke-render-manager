# ui.py

import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QDialog,
    QLineEdit, QCheckBox, QMessageBox, QFileDialog, QTextEdit, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor

from job import Job
from queue_manager import QueueManager
import runner


# ─────────────────────────────────────────────
#  THREAD — roda a fila sem travar a interface
# ─────────────────────────────────────────────

class RenderThread(QThread):
    job_status_changed = Signal(object)  # Sinal enviado quando um job muda de status
    queue_finished     = Signal()        # Sinal enviado quando a fila termina
    log_line = Signal(str)

    def __init__(self, queue_manager):
        super().__init__()
        self.queue_manager = queue_manager

    def run(self):
        """ Este método roda na thread separada """
        runner.run_queue(
            self.queue_manager, 
            on_status_change=self.job_status_changed.emit,
            on_log=self.log_line.emit
        )
        self.queue_finished.emit()


# ─────────────────────────────────────────────
#  DIÁLOGO — formulário para adicionar job
# ─────────────────────────────────────────────

class AddJobDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Job")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Campo: caminho do .nk
        layout.addWidget(QLabel("Arquivo .nk:"))
        path_layout = QHBoxLayout()
        self.nk_path_input = QLineEdit()
        self.nk_path_input.setPlaceholderText("C:/projetos/cena.nk")
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.nk_path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Campo: writes
        layout.addWidget(QLabel("Write nodes (separados por espaço — deixe vazio para todos):"))
        self.writes_input = QLineEdit()
        self.writes_input.setPlaceholderText("Write1 Write_EXR Write_DPX")
        layout.addWidget(self.writes_input)

        # Campo: frame range
        layout.addWidget(QLabel("Frame range (opcional — ex: 1001-1100):"))
        self.frame_range_input = QLineEdit()
        self.frame_range_input.setPlaceholderText("1001-1100")
        layout.addWidget(self.frame_range_input)

        # Botões OK / Cancelar
        btn_layout = QHBoxLayout()
        ok_btn     = QPushButton("Adicionar")
        cancel_btn = QPushButton("Cancelar")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        """ Abre o explorador de arquivos para selecionar o .nk """
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar .nk", "", "Nuke Scripts (*.nk)")
        if path:
            self.nk_path_input.setText(path)

    def get_job(self):
        """ Lê os campos e retorna um Job, ou None se o path estiver vazio """
        nk_path = self.nk_path_input.text().strip()
        if not nk_path:
            return None

        writes_text = self.writes_input.text().strip()
        writes      = writes_text.split() if writes_text else []

        frame_range = self.frame_range_input.text().strip() or None

        return Job(nk_path, writes, frame_range)


# ─────────────────────────────────────────────
#  JANELA PRINCIPAL
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuke Render Manager")
        self.setMinimumSize(700, 450)

        self.queue_manager = QueueManager()
        self.render_thread = None

        self._build_ui()
        self._refresh_list()

    def _log(self, text):
        # Adiciona uma linha no painel de log
        self.log_output.append(text)
        #Scrolla automaticamente pro final
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )



    def archive_done_jobs(self):
        self.queue_manager.archive_done_jobs()
        self._refresh_list()
        self.status_label.setText("Jobs concluídos aqruivados.")
        self._refresh_done_list()
        self.status_label.setText("Jobs concluídos arquivados.")



    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        #cria widget de abas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)


        #aba render
        render_tab = QWidget()
        main_layout = QVBoxLayout(render_tab)

        splitter = QSplitter(Qt.Vertical)

        # Lista de jobs
        self.job_list = QListWidget()
        self.job_list.setStyleSheet("""
            QListWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
            }
        """)

        splitter.addWidget(self.job_list)

        # Painel de log

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: Consolas, monospace;
                font-size: 11px;
                border: 1px solid #555555;
            }
        """)
        self.log_output.setMinimumHeight(120)
        splitter.addWidget(self.log_output)

        splitter.setSizes([300, 150])
        main_layout.addWidget(splitter, stretch=1)

        # Botões de controle da fila
        btn_layout = QHBoxLayout()

        self.add_btn    = QPushButton("+ Adicionar Job")
        self.remove_btn = QPushButton("− Remover")
        self.up_btn     = QPushButton("↑ Subir")
        self.down_btn   = QPushButton("↓ Descer")
        self.start_btn  = QPushButton("▶ Iniciar Fila")
        self.archive_btn = QPushButton("Arquivar Concluídos")

        self.add_btn.clicked.connect(self.add_job)
        self.remove_btn.clicked.connect(self.remove_job)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        self.start_btn.clicked.connect(self.start_queue)
        self.archive_btn.clicked.connect(self.archive_done_jobs)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        btn_layout.addStretch()  # Empurra o botão iniciar para a direita
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.archive_btn)

        main_layout.addLayout(btn_layout)

        # Barra de status
        self.status_label = QLabel("Pronto.")
        main_layout.addWidget(self.status_label)

        self.tabs.addTab(render_tab, "Render")



        # Aba Done

        done_tab = QWidget()
        done_layout = QVBoxLayout(done_tab)

        self.done_list = QListWidget()
        self.done_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
            }
            """)
        done_layout.addWidget(self.done_list, stretch=1)



        # botao para limpar historico

        clear_btn = QPushButton("Limpar Histórico")
        clear_btn.clicked.connect(self._clear_done_history)
        done_layout.addWidget(clear_btn)


        self.tabs.addTab(done_tab, "Done")


        self._refresh_done_list()

    def _refresh_list(self, keep_selected_id=None):
        """ Redesenha a lista de jobs na tela """
        self.job_list.clear()
        for i, job in enumerate(self.queue_manager.jobs):
            writes_text = ", ".join(job.writes) if job.writes else "All Writes"
            range_text  = job.frame_range if job.frame_range else "project range"
            label       = f"[{job.status.upper()}]  {job.nk_path}  |  {writes_text}  |  {range_text}"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, job.id)

            colors = {
                "waiting" : QColor("#2b2b2b"),
                "running" : QColor("#5a4a00"),
                "done"    : QColor("#1a4a1a"),
                "error"   : QColor("#4a1a1a"),
            }
            item.setBackground(colors.get(job.status, QColor("#2b2b2b")))
            item.setForeground(QColor("#ffffff"))

            self.job_list.addItem(item)

            # Restaura a seleçao apos refresh
            if job.id == keep_selected_id:
                self.job_list.setCurrentRow(i)


    def _refresh_done_list(self):
        # Atualiza a lista de jobs concluidos

        self.done_list.clear()

        if not os.path.exists("done.json"):
            return
        
        with open("done.json", "r") as f:
            done_jobs = json.load(f)


        for job_data in reversed(done_jobs):
            writes_text = ", ".join(job_data["writes"]) if job_data["writes"] else "All Writes"
            range_text = job_data["frame_range"] if job_data["frame_range"] else "project range"
            label = f"{job_data['nk_path']} | {writes_text} | {range_text}"
            item = QListWidgetItem(label)
            item.setForeground(QColor("#ffffff"))
            self.done_list.addItem(item)



    def _clear_done_history(self):
        # Apaga o done.json e limpa a lista

        if os.path.exists("done.json"):
            os.remove("done.json")

        self.done_list.clear()
        self.status_label.setText("Histórico limpo.")

    def _selected_job_id(self):
        """ Retorna o ID do job selecionado na lista, ou None """
        item = self.job_list.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None
    


    # ── Ações dos botões ──

    def add_job(self):
        dialog = AddJobDialog(self)
        if dialog.exec():
            job = dialog.get_job()
            if job:
                self.queue_manager.add_job(job)
                self._refresh_list()

    def remove_job(self):
        job_id = self._selected_job_id()
        if job_id:
            self.queue_manager.remove_job(job_id)
            self._refresh_list()

    def move_up(self):
        job_id = self._selected_job_id()
        if job_id:
            self.queue_manager.move_up(job_id)
            self._refresh_list(keep_selected_id=job_id)

    def move_down(self):
        job_id = self._selected_job_id()
        if job_id:
            self.queue_manager.move_down(job_id)
            self._refresh_list(keep_selected_id=job_id)

    def start_queue(self):
        if self.render_thread and self.render_thread.isRunning():
            QMessageBox.warning(self, "Aviso", "A fila já está rodando.")
            return

        self.render_thread = RenderThread(self.queue_manager)
        self.render_thread.job_status_changed.connect(self._on_status_change)
        self.render_thread.queue_finished.connect(self._on_queue_finished)
        self.render_thread.log_line.connect(self._log)
        self.render_thread.start()

        self.start_btn.setEnabled(False)
        self.status_label.setText("Renderizando...")

    def _on_status_change(self, job):
        """ Chamado pela thread quando um job muda de status """
        self._refresh_list()
        self.status_label.setText(f"Rodando: {job.nk_path}")

    def _on_queue_finished(self):
        """ Chamado pela thread quando a fila termina """
        self.queue_manager.save()
        self._refresh_list()
        self.start_btn.setEnabled(True)
        self.status_label.setText("Fila concluída.")