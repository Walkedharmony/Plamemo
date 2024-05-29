import sys
import os
import subprocess
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QTextEdit, QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton
from PyQt5.QtGui import QFont, QIcon

# Setup logging
logging.basicConfig(filename='vntextpatch_gui.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VNTextPatchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('VNTextPatch GUI')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('Icon1.ico'))

        # Menyiapkan widget utama
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout utama
        self.layout = QVBoxLayout(self.central_widget)

        # Label status
        self.status_label = QLabel('')
        self.layout.addWidget(self.status_label)
        
        # Area teks untuk log
        self.log_area = QTextEdit()
        self.log_area.setFont(QFont('Courier', 10))
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)
        
        # Tombol Jalankan VNTextPatch
        self.run_button = QPushButton('Run VNTextPatch', self)
        self.run_button.clicked.connect(self.confirm_run_vntextpatch)
        self.layout.addWidget(self.run_button)
        
        # Tombol untuk membuka folder dump
        self.open_folder_button = QPushButton('Buka Folder Dump', self)
        self.open_folder_button.clicked.connect(self.open_dump_folder)
        self.layout.addWidget(self.open_folder_button)

        # Menu
        menubar = self.menuBar()

        # Menu File
        file_menu = menubar.addMenu('File')

        # Menu Ekspor
        export_action = QAction('Pilih Folder SCN', self)
        export_action.triggered.connect(self.browse_source_folder)
        file_menu.addAction(export_action)

        # Menu Dump
        dump_action = QAction('Pilih Destinasi Folder', self)
        dump_action.triggered.connect(self.browse_dump_folder)
        file_menu.addAction(dump_action)

        # Menu Impor
        import_action = QAction('Ubah Kembali Ke SCN', self)
        import_action.triggered.connect(self.import_from_dump)
        file_menu.addAction(import_action)
        
    def browse_source_folder(self):
        try:
            options = QFileDialog.Options()
            folder_name = QFileDialog.getExistingDirectory(self, "Pilih Folder SCN", options=options)
            if folder_name:
                self.source_folder_path = folder_name
                logging.info(f'Source folder selected: {folder_name}')
        except Exception as e:
            logging.error(f'Failed to open source folder: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal membuka Pilih Folder SCN: {str(e)}')
    
    def browse_dump_folder(self):
        try:
            options = QFileDialog.Options()
            folder_name = QFileDialog.getExistingDirectory(self, "Pilih Folder Dump", options=options)
            if folder_name:
                self.dump_folder_path = folder_name
                logging.info(f'Dump folder selected: {folder_name}')
        except Exception as e:
            logging.error(f'Failed to open dump folder: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal membuka folder dump: {str(e)}')
    
    def confirm_run_vntextpatch(self):
        try:
            if not hasattr(self, 'source_folder_path') or not os.path.isdir(self.source_folder_path):
                QMessageBox.warning(self, 'Error', 'Folder SCN tidak ditemukan!')
                return
            if not hasattr(self, 'dump_folder_path') or not os.path.isdir(self.dump_folder_path):
                QMessageBox.warning(self, 'Error', 'Folder dump tidak ditemukan!')
                return
            
            reply = QMessageBox.question(self, 'Konfirmasi', 
                                         'Apakah Anda yakin ingin memproses semua file dalam folder ini?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.run_vntextpatch()
        except Exception as e:
            logging.error(f'Failed to confirm running VNTextPatch: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal mengkonfirmasi jalankan VNTextPatch: {str(e)}')

    def run_vntextpatch(self):
        try:
            self.status_label.setText('Memproses...')
            vntextpatch_path = resource_path('VN_Editor/VNTextPatch.exe')
            command = f'"{vntextpatch_path}" extractlocal "{self.source_folder_path}" "{self.dump_folder_path}"'
            logging.info(f'Running command: {command}')
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == b"" and process.poll() is not None:
                    break
                if output:
                    self.log_area.append(output.decode('utf-8'))
            stderr = process.stderr.read()
            if process.returncode == 0:
                self.status_label.setText('Proses selesai!')
                self.log_area.append('Proses selesai tanpa error.')
                logging.info('VNTextPatch ran successfully.')
            else:
                self.status_label.setText('Proses selesai dengan error!')
                self.log_area.append('Terjadi error selama proses.')
                self.log_area.append(stderr.decode('utf-8'))
                logging.error(f'Error running VNTextPatch: {stderr.decode()}')
        except Exception as e:
            logging.error(f'Failed to run VNTextPatch: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal menjalankan VNTextPatch: {str(e)}')
            self.log_area.append(f'Error: {str(e)}')
    
    def open_dump_folder(self):
        try:
            if not hasattr(self, 'dump_folder_path') or not os.path.isdir(self.dump_folder_path):
                QMessageBox.warning(self, 'Error', 'Folder dump tidak ditemukan!')
                return
            os.startfile(self.dump_folder_path)
            self.status_label.setText(f'Folder dump dibuka: {self.dump_folder_path}')
            logging.info(f'Opened dump folder: {self.dump_folder_path}')
        except Exception as e:
            logging.error(f'Failed to open dump folder: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal membuka folder dump: {str(e)}')
            self.status_label.setText(f'Gagal membuka folder dump: {str(e)}')

    def import_from_dump(self):
        try:
            if not hasattr(self, 'source_folder_path') or not os.path.isdir(self.source_folder_path):
                QMessageBox.warning(self, 'Error', 'Pilih Folder SCN tidak ditemukan!')
                return
            if not hasattr(self, 'dump_folder_path') or not os.path.isdir(self.dump_folder_path):
                QMessageBox.warning(self, 'Error', 'Folder dump tidak ditemukan!')
                return
            
            options = QFileDialog.Options()
            dest_folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Destinasi Output", options=options)
            if not dest_folder_path:
                return

            self.status_label.setText('Mengimpor...')
            vntextpatch_path = resource_path('VN_Editor/VNTextPatch.exe')
            command = f'"{vntextpatch_path}" insertlocal "{self.source_folder_path}" "{self.dump_folder_path}" "{dest_folder_path}"'
            logging.info(f'Running command: {command}')
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == b"" and process.poll() is not None:
                    break
                if output:
                    self.log_area.append(output.decode('utf-8'))
            stderr = process.stderr.read()
            if process.returncode == 0:
                self.status_label.setText('Impor selesai!')
                self.log_area.append('Impor selesai tanpa error.')
                logging.info('Import ran successfully.')
            else:
                self.status_label.setText('Impor selesai dengan error!')
                self.log_area.append('Terjadi error selama impor.')
                self.log_area.append(stderr.decode('utf-8'))
                logging.error(f'Error running import: {stderr.decode()}')
        except Exception as e:
            logging.error(f'Failed to import from dump: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal mengimpor dari dump: {str(e)}')
            self.log_area.append(f'Error: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VNTextPatchGUI()
    ex.show()
    sys.exit(app.exec_())
