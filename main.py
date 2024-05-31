import sys
import os
import subprocess
import shutil
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QTextEdit, 
                             QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton, 
                             QListWidget, QDialog)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Setup logging
logging.basicConfig(filename='vntextpatch_gui.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

class CommandExecutor:
    def __init__(self):
        pass

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FileSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super(FileSelectorDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dumper')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('VN_Editor/Icon1.ico'))

        self.layout = QVBoxLayout(self)

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        self.open_source_folder_button = QPushButton('Pilih Folder Sumber', self)
        self.open_source_folder_button.clicked.connect(self.browse_source_folder)
        self.layout.addWidget(self.open_source_folder_button)

        self.decompile_all_button = QPushButton('Decompile all File', self)
        self.decompile_all_button.clicked.connect(self.decompile_all_files)
        self.layout.addWidget(self.decompile_all_button)
        
        self.run_button = QPushButton('Decompile File Yang Dipilih', self)
        self.run_button.clicked.connect(self.run_command_on_selected_file)
        self.layout.addWidget(self.run_button)

    def browse_source_folder(self):
        try:
            options = QFileDialog.Options()
            folder_name = QFileDialog.getExistingDirectory(self, "Cari Folder windata", options=options)
            if folder_name:
                self.folder_path = folder_name
                self.load_files(folder_name)
                logging.info(f'Source folder selected: {folder_name}')
                QMessageBox.information(self, 'Folder Selected', f'Source folder selected: {folder_name}')
        except Exception as e:
            logging.error(f'Failed to open source folder: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal membuka Pilih Folder SCN: {str(e)}')
    
    def load_files(self, folder_path):
        try:
            files = os.listdir(folder_path)
            self.file_list.clear()
            for file in files:
                if file.endswith('.psb.m') and os.path.isfile(os.path.join(folder_path, file)):
                    self.file_list.addItem(file)
            logging.info(f'Files loaded from {folder_path}')
        except Exception as e:
            logging.error(f'Failed to load files: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Gagal memuat file: {str(e)}')   

    def decompile_all_files(self):
        for i in range(self.file_list.count()):
            psbdecompile_path = resource_path('FreeMote/psbdecompile.exe')
            key = '38757621acf82'
            item = self.file_list.item(i)
            file_name = item.text()
            file_path = os.path.join(self.folder_path, file_name)
            command = f'{psbdecompile_path} info-psb -k {key} "{file_path}"'
            subprocess.run(command, shell=True, check=True)
            self.post_decompile_steps(file_path)
        QMessageBox.information(self, 'Success', 'All files decompiled successfully')
        logging.info('All files decompiled successfully')

    def run_command_on_selected_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            file_path = os.path.join(self.folder_path, file_name)
            self.execute_command(file_path)
        else:
            QMessageBox.warning(self, 'Warning', 'Tidak ada file yang dipilih')

    def execute_command(self, file_path):
        try:
            psbdecompile_path = resource_path('FreeMote/psbdecompile.exe')
            command = f'{psbdecompile_path} info-psb -k 38757621acf82 "{file_path}"'
            logging.info(f'Executing command: {command}')
            subprocess.run(command, shell=True)
            QMessageBox.information(self, 'Success', f'Command executed successfully on {file_path}')
            logging.info(f'Command executed successfully on {file_path}')
            self.post_decompile_steps(file_path)
        except Exception as e:
            logging.error(f'Error executing command on {file_path}: {e}')
            QMessageBox.critical(self, 'Error', f'Failed to execute command on {file_path}')

    def post_decompile_steps(self, file_path):
        try:
            dump_folder = os.path.join(os.path.dirname(file_path), 'dump')
            os.makedirs(dump_folder, exist_ok=True)
            logging.info(f'Dump folder created at {dump_folder}')

            folders_to_check = ['Config', 'Scenario', 'Motion', 'Sound', 'Voice', 'Image', 'Font', 'Script', 'Patch']
            for folder in folders_to_check:
                src_folder = os.path.join(os.path.dirname(file_path), folder)
                if os.path.isdir(src_folder):
                    shutil.move(src_folder, os.path.join(dump_folder, folder))
                    logging.info(f'{folder} folder moved to {dump_folder}')

            for folder in folders_to_check:
                bat_file = os.path.join(dump_folder, folder, 'remove_m.bat')
                if os.path.isdir(os.path.join(dump_folder, folder)):
                    with open(bat_file, 'w') as bat:
                        bat.write('ren *.m *.')
                    logging.info(f'.bat file created at {bat_file}')

            json_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.endswith('.json')]
            for json_file in json_files:
                shutil.move(os.path.join(os.path.dirname(file_path), json_file), dump_folder)
                logging.info(f'{json_file} file moved to {dump_folder}')

            for folder in folders_to_check:
                bat_file = os.path.join(dump_folder, folder, 'remove_m.bat')
                if os.path.isdir(os.path.join(dump_folder, folder)):
                    with open(bat_file, 'w') as bat:
                        bat.write('ren *.m *.')
                    logging.info(f'.bat file created at {bat_file}')
        except Exception as e:
            logging.error(f'Error during post decompile steps: {e}')
            QMessageBox.critical(self, 'Error', 'Failed during post decompile steps')
            
            # Run the .bat file
            #subprocess.run([bat_file_config], shell=True)
            #logging.info(f'.bat file executed at {bat_file_config}')
            #QMessageBox.information(self, 'Success', f'.bat file executed successfully')

class VNTextPatchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Plamemo CORE')
        self.setGeometry(100, 100, 960, 544)
        self.setWindowIcon(QIcon('VN_Editor/Icon1.ico'))

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
        self.log_area.setStyleSheet("background-color: black; color: white;")
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
        file_menu = menubar.addMenu('Ekspor File SCN')

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

        # Menu File Selector
        file_menu = menubar.addMenu('Decompile')
        file_selector_action = QAction('Dumper Plamemo', self)
        file_selector_action.triggered.connect(self.open_file_selector)
        file_menu.addAction(file_selector_action)
        
    def open_file_selector(self):
        self.file_selector_dialog = FileSelectorDialog(self)
        self.file_selector_dialog.exec_()
        
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
