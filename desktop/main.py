import sys
import requests
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QMessageBox, QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

API_URL = "http://127.0.0.1:8000/api"

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(ChartCanvas, self).__init__(self.fig)
        self.fig.patch.set_facecolor('#1e1b4b')
        self.ax.set_facecolor('#1e1b4b')

    def plot_dist(self, distribution):
        self.ax.clear()
        labels = list(distribution.keys())
        values = list(distribution.values())
        colors = ['#4f46e5', '#818cf8', '#c084fc', '#e879f9', '#f472b6', '#fb7185']
        
        self.ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, 
                   textprops={'color':"w"})
        self.ax.set_title("Equipment Type Distribution", color='w')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemVis Desktop | Equipment Visualizer")
        self.setMinimumSize(1000, 700)
        self.auth_header = None
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Login Overlay simulation or separate stack
        self.setup_login_ui()
        self.setup_main_ui()
        
        self.main_stack = QVBoxLayout()
        self.main_layout.addLayout(self.main_stack)
        
        self.show_login()

    def setup_login_ui(self):
        self.login_widget = QWidget()
        layout = QVBoxLayout(self.login_widget)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(400, 300)
        card.setStyleSheet("background-color: #1e293b; border-radius: 15px; border: 1px solid #334155;")
        card_layout = QVBoxLayout(card)

        title = QLabel("Authentication")
        title.setFont(QFont("Inter", 18, QFont.Bold))
        title.setStyleSheet("color: white; border: none;")
        card_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setStyleSheet("padding: 10px; background: #0f172a; color: white;")
        card_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("padding: 10px; background: #0f172a; color: white;")
        card_layout.addWidget(self.pass_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("background: #4f46e5; color: white; padding: 12px; font-weight: bold;")
        card_layout.addWidget(login_btn)

        layout.addWidget(card)

    def setup_main_ui(self):
        self.app_widget = QWidget()
        self.app_layout = QHBoxLayout(self.app_widget)

        # Left Panel (History & Upload)
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("background: #0f172a; border-right: 1px solid #334155;")
        left_layout = QVBoxLayout(left_panel)

        upload_btn = QPushButton("Upload CSV")
        upload_btn.clicked.connect(self.handle_upload)
        upload_btn.setStyleSheet("background: #4f46e5; color: white; padding: 10px; margin-bottom: 20px;")
        left_layout.addWidget(upload_btn)

        left_layout.addWidget(QLabel("Last 5 Uploads", styleSheet="color: #94a3b8; font-weight: bold;"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_historical_dataset)
        left_layout.addWidget(self.history_list)

        # Right Panel (Dashboard)
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)

        # Stats
        stats_layout = QHBoxLayout()
        self.stat_labels = {}
        for s in ["Total Count", "Avg Flow", "Avg Press", "Avg Temp"]:
            v_layout = QVBoxLayout()
            lbl = QLabel(s, styleSheet="color: #94a3b8; font-size: 10px;")
            val = QLabel("0", styleSheet="font-size: 18px; font-weight: bold; color: white;")
            self.stat_labels[s] = val
            v_layout.addWidget(lbl)
            v_layout.addWidget(val)
            stats_layout.addLayout(v_layout)
        self.right_layout.addLayout(stats_layout)

        # Chart
        self.canvas = ChartCanvas(self, width=5, height=3)
        self.right_layout.addWidget(self.canvas)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flow", "Press", "Temp"])
        self.table.setStyleSheet("background: #1e293b; color: white;")
        self.right_layout.addWidget(self.table)

        # PDF Button
        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setStyleSheet("background: #10b981; color: white; padding: 8px;")
        self.right_layout.addWidget(self.pdf_btn)

        self.app_layout.addWidget(left_panel)
        self.app_layout.addWidget(right_panel)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: white; }
            QPushButton { border-radius: 5px; }
            QTableWidget { gridline-color: #334155; }
            QHeaderView::section { background-color: #334155; color: white; padding: 5px; }
        """)

    def show_login(self):
        self.main_stack.addWidget(self.login_widget)
        if hasattr(self, 'app_widget'): self.app_widget.hide()

    def handle_login(self):
        user = self.user_input.text()
        pw = self.pass_input.text()
        auth_str = f"{user}:{pw}"
        self.auth_header = {"Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode()}
        
        try:
            r = requests.get(f"{API_URL}/history/", headers=self.auth_header)
            if r.status_code == 200:
                self.login_widget.hide()
                self.main_stack.addWidget(self.app_widget)
                self.app_widget.show()
                self.refresh_history()
            else:
                QMessageBox.critical(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {e}")

    def refresh_history(self):
        r = requests.get(f"{API_URL}/history/", headers=self.auth_header)
        data = r.json()
        self.history_list.clear()
        self.current_history_data = data
        for item in data:
            list_item = QListWidgetItem(f"{item['filename']}\n{item['upload_date'][:16]}")
            list_item.setData(Qt.UserRole, item['id'])
            self.history_list.addItem(list_item)

    def load_historical_dataset(self, item):
        ds_id = item.data(Qt.UserRole)
        # Find in current_history_data
        dataset = next((d for d in self.current_history_data if d['id'] == ds_id), None)
        if dataset:
            self.display_data(dataset)

    def handle_upload(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV files (*.csv)")
        if fname:
            with open(fname, 'rb') as f:
                r = requests.post(f"{API_URL}/upload/", headers=self.auth_header, files={'file': f})
                if r.status_code == 201:
                    self.display_data(r.json())
                    self.refresh_history()
                else:
                    QMessageBox.warning(self, "Error", r.json().get('error', 'Upload failed'))

    def display_data(self, data):
        self.current_dataset_id = data['id']
        stats = data['summary_stats']
        self.stat_labels["Total Count"].setText(str(stats['total_count']))
        self.stat_labels["Avg Flow"].setText(f"{stats['avg_flowrate']:.2f}")
        self.stat_labels["Avg Press"].setText(f"{stats['avg_pressure']:.2f}")
        self.stat_labels["Avg Temp"].setText(f"{stats['avg_temperature']:.2f}")

        self.canvas.plot_dist(stats['type_distribution'])

        self.table.setRowCount(len(data['items']))
        for i, item in enumerate(data['items']):
            self.table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.table.setItem(i, 1, QTableWidgetItem(item['equipment_type']))
            self.table.setItem(i, 2, QTableWidgetItem(str(item['flowrate'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(item['pressure'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(item['temperature'])))

    def download_pdf(self):
        if not hasattr(self, 'current_dataset_id'): return
        r = requests.get(f"{API_URL}/report/{self.current_dataset_id}/", headers=self.auth_header)
        if r.status_code == 200:
            path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"report_{self.current_dataset_id}.pdf", "PDF files (*.pdf)")
            if path:
                with open(path, 'wb') as f:
                    f.write(r.content)
                QMessageBox.information(self, "Success", "Report saved successfully")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
