from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QCalendarWidget, 
    QFrame, QGroupBox, QComboBox, QTimeEdit, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QUrl, QTime, QTimer
from PySide6.QtGui import QDesktopServices, QColor, QIcon
import sqlite3
import re
import os
from datetime import datetime, timedelta

class CRMPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.check_database() # Garante que a tabela existe
        self.init_ui()
        
        # --- ROBÔ DE ALERTA (TIMER) ---
        # Verifica a agenda a cada 60 segundos (60000 ms)
        self.timer_alerta = QTimer(self)
        self.timer_alerta.timeout.connect(self.verificar_agendamentos_proximos)
        self.timer_alerta.start(60000) 

    def check_database(self):
        """Cria a tabela de agendamentos se não existir"""
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                service TEXT,
                phone TEXT,
                date_str TEXT,
                time_str TEXT,
                status TEXT DEFAULT 'Agendado'
            )
        """)
        conn.commit()
        conn.close()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- COLUNA DA ESQUERDA ---
        left_col = QVBoxLayout()
        
        # Calendário Profissional
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { alternate-background-color: #f0f0f0; }
            QCalendarWidget QToolButton { color: black; icon-size: 24px; font-weight: bold; }
            QCalendarWidget QAbstractItemView:enabled { font-size: 14px; color: #333; selection-background-color: #2980b9; }
        """)
        self.calendar.clicked.connect(self.load_schedule) # Ao clicar, carrega o dia
        left_col.addWidget(self.calendar)

        # Formulário
        group_add = QGroupBox("📅 Novo Agendamento")
        group_add.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #aaa; margin-top: 10px; }")
        form_lay = QVBoxLayout(group_add)
        
        self.inp_cliente = QLineEdit(); self.inp_cliente.setPlaceholderText("Nome da Cliente")
        self.inp_servico = QComboBox()
        self.inp_servico.addItems(["Corte Feminino", "Escova", "Manicure", "Pedicure", "Coloração", "Progressiva", "Maquiagem", "Barba (Masc)"])
        self.inp_hora = QTimeEdit(QTime.currentTime()); self.inp_hora.setDisplayFormat("HH:mm")
        self.inp_zap = QLineEdit(); self.inp_zap.setPlaceholderText("WhatsApp (Ex: 16991234567)")

        form_lay.addWidget(QLabel("Cliente:")); form_lay.addWidget(self.inp_cliente)
        form_lay.addWidget(QLabel("WhatsApp:")); form_lay.addWidget(self.inp_zap)
        form_lay.addWidget(QLabel("Serviço:")); form_lay.addWidget(self.inp_servico)
        form_lay.addWidget(QLabel("Horário:")); form_lay.addWidget(self.inp_hora)
        
        btn_schedule = QPushButton("✅ Agendar Horário")
        btn_schedule.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 6px;")
        btn_schedule.setCursor(Qt.PointingHandCursor)
        btn_schedule.clicked.connect(self.add_schedule)
        form_lay.addWidget(btn_schedule)
        
        left_col.addWidget(group_add)
        left_col.addStretch()
        
        # --- COLUNA DA DIREITA (AGENDA) ---
        right_col = QVBoxLayout()
        
        self.lbl_date = QLabel(f"Agenda de: {QDate.currentDate().toString('dd/MM/yyyy')}")
        self.lbl_date.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        right_col.addWidget(self.lbl_date)
        
        self.table_agenda = QTableWidget(0, 6) # ID oculto na col 5
        self.table_agenda.setHorizontalHeaderLabels(["Hora", "Cliente", "Serviço", "Contato", "Ações", "ID"])
        self.table_agenda.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_agenda.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_agenda.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_agenda.setColumnHidden(5, True) # Esconde o ID
        self.table_agenda.setAlternatingRowColors(True)
        right_col.addWidget(self.table_agenda)
        
        # Botão de Alerta para o Usuário
        btn_check_msg = QPushButton("🔔 Verificar Novas Mensagens (Zap)")
        btn_check_msg.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_check_msg.setCursor(Qt.PointingHandCursor)
        btn_check_msg.clicked.connect(lambda: QMessageBox.information(self, "Lembrete", "Abra o WhatsApp Web/Desktop para verificar se há novas mensagens de clientes!"))
        right_col.addWidget(btn_check_msg)

        # Botões de Ação em Massa
        btn_box = QHBoxLayout()
        btn_zap_all = QPushButton("📢 Lembrete Geral (Zap)")
        btn_zap_all.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        btn_zap_all.clicked.connect(self.blast_reminders) # Agora a função existe!
        
        btn_cancel = QPushButton("🗑️ Excluir Agendamento")
        btn_cancel.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 10px;")
        btn_cancel.clicked.connect(self.delete_schedule)
        
        btn_box.addWidget(btn_zap_all)
        btn_box.addWidget(btn_cancel)
        right_col.addLayout(btn_box)

        layout.addLayout(left_col, 1)
        layout.addLayout(right_col, 2)
        
        # Carrega agenda de hoje ao abrir
        self.load_schedule()

    def load_schedule(self):
        """Carrega os dados do banco para a data selecionada"""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.lbl_date.setText(f"Agenda de: {self.calendar.selectedDate().toString('dd/MM/yyyy')}")
        
        self.table_agenda.setRowCount(0)
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("SELECT time_str, client_name, service, phone, id FROM appointments WHERE date_str = ? ORDER BY time_str", (selected_date,))
            rows = cursor.fetchall()
            conn.close()
            
            # Tenta achar o ícone do WhatsApp
            icon_path = os.path.join("src", "app", "assets", "icon", "whatsapp.png")
            has_icon = os.path.exists(icon_path)
            
            for row_data in rows:
                hora, nome, servico, zap, app_id = row_data
                row = self.table_agenda.rowCount()
                self.table_agenda.insertRow(row)
                
                self.table_agenda.setItem(row, 0, QTableWidgetItem(hora))
                self.table_agenda.setItem(row, 1, QTableWidgetItem(nome))
                self.table_agenda.setItem(row, 2, QTableWidgetItem(servico))
                self.table_agenda.setItem(row, 3, QTableWidgetItem(zap))
                self.table_agenda.setItem(row, 5, QTableWidgetItem(str(app_id))) # ID Oculto
                
                # Botão Zap
                container = QWidget()
                lay = QHBoxLayout(container); lay.setContentsMargins(2, 2, 2, 2)
                
                btn_zap = QPushButton()
                btn_zap.setToolTip(f"Enviar mensagem para {nome}")
                btn_zap.setCursor(Qt.PointingHandCursor)
                
                if has_icon:
                    btn_zap.setIcon(QIcon(icon_path))
                    btn_zap.setIconSize(Qt.QSize(24, 24))
                    btn_zap.setStyleSheet("border: none; background: transparent;")
                else:
                    btn_zap.setText("Zap")
                    btn_zap.setStyleSheet("background-color: #25D366; color: white; font-weight: bold; border-radius: 4px; padding: 5px;")
                
                # Agora chama self.open_whatsapp corretamente
                btn_zap.clicked.connect(lambda _, z=zap, n=nome, s=servico, h=hora: self.open_whatsapp(z, n, s, h))
                lay.addWidget(btn_zap)
                self.table_agenda.setCellWidget(row, 4, container)
                
        except Exception as e:
            print(f"Erro ao carregar agenda: {e}")

    def add_schedule(self):
        cli = self.inp_cliente.text().strip()
        serv = self.inp_servico.currentText()
        hora = self.inp_hora.time().toString("HH:mm")
        zap = self.inp_zap.text().strip()
        data = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        if not cli:
            QMessageBox.warning(self, "Erro", "Digite o nome da cliente!")
            return
            
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointments (client_name, service, phone, date_str, time_str)
                VALUES (?, ?, ?, ?, ?)
            """, (cli, serv, zap, data, hora))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Agendado", f"{cli} agendada para {hora}!")
            self.inp_cliente.clear()
            self.inp_zap.clear()
            self.load_schedule() # Recarrega a tabela
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def delete_schedule(self):
        row = self.table_agenda.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente na tabela para excluir.")
            return
            
        app_id = self.table_agenda.item(row, 5).text()
        cliente = self.table_agenda.item(row, 1).text()
        
        if QMessageBox.question(self, "Excluir", f"Cancelar horário de {cliente}?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id = ?", (app_id,))
            conn.commit()
            conn.close()
            self.load_schedule()

    # --- NOVAS FUNÇÕES (ESTAVAM FALTANDO) ---

    def open_whatsapp(self, phone, name, service, time):
        """Abre o WhatsApp Web com mensagem personalizada"""
        clean_phone = re.sub(r'\D', '', str(phone))
        
        if not clean_phone:
            QMessageBox.warning(self, "Erro", "Telefone inválido ou não cadastrado.")
            return
            
        # Adiciona 55 se parecer número BR sem DDI
        if len(clean_phone) <= 11 and not clean_phone.startswith("55"):
            clean_phone = "55" + clean_phone
            
        msg = f"Olá {name}, passando para confirmar seu horário de {service} hoje às {time}. Tudo certo? 😊"
        url = f"https://wa.me/{clean_phone}?text={msg}"
        QDesktopServices.openUrl(QUrl(url))

    def blast_reminders(self):
        """Disparo em Massa (Simulado/Demo)"""
        rows = self.table_agenda.rowCount()
        if rows == 0:
            QMessageBox.information(self, "Vazio", "Nenhum cliente na agenda de hoje.")
            return
            
        msg = QMessageBox()
        msg.setWindowTitle("Disparo em Massa")
        msg.setText(f"O sistema encontrou {rows} clientes hoje.\n\nDeseja abrir o WhatsApp para confirmar com todos?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            # Em produção, usaria API. Aqui abrimos o primeiro da lista como exemplo.
            primeiro_zap = self.table_agenda.item(0, 3).text()
            primeiro_nome = self.table_agenda.item(0, 1).text()
            primeiro_hora = self.table_agenda.item(0, 0).text()
            
            if primeiro_zap:
                self.open_whatsapp(primeiro_zap, primeiro_nome, "Serviço", primeiro_hora)
            else:
                QMessageBox.warning(self, "Erro", "O primeiro cliente não tem WhatsApp cadastrado.")

    # --- ROBÔ DE ALERTA ---
    def verificar_agendamentos_proximos(self):
        """Roda a cada 1 min para ver se tem alguém chegando"""
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            
            hoje = datetime.now().strftime("%Y-%m-%d")
            agora = datetime.now()
            
            # Pega agendamentos de hoje
            cursor.execute("SELECT client_name, time_str FROM appointments WHERE date_str = ?", (hoje,))
            compromissos = cursor.fetchall()
            conn.close()
            
            for nome, hora_str in compromissos:
                # Converte hora do banco para objeto datetime
                hora_agenda = datetime.strptime(f"{hoje} {hora_str}", "%Y-%m-%d %H:%M")
                
                # Calcula diferença
                diferenca = hora_agenda - agora
                
                # Se faltar entre 0 e 15 minutos (900 segundos)
                # E evita alertas passados
                segundos_restantes = diferenca.total_seconds()
                
                if 0 < segundos_restantes <= 900:
                    self.show_popup_alerta(f"⏰ ATENÇÃO: {nome} está agendada para {hora_str}!\nVerifique se já confirmou no WhatsApp.")
                    
        except Exception as e:
            print(f"Erro no robô de alerta: {e}")

    def show_popup_alerta(self, texto):
        """Mostra um pop-up que fica por cima de tudo"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Lembrete Automático")
        msg.setText(texto)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowFlags(Qt.WindowStaysOnTopHint) # Força ficar no topo
        msg.show()