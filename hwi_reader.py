import sys
import zipfile
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QFileDialog, QLabel, QGridLayout, QScrollArea)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import fitz  # rendering pdf

class AcrobatReader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acrobat Reader - HWI Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.current_page = 0
        self.doc = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.load_button = QPushButton("Load .HWI File")
        self.load_button.clicked.connect(self.load_hwi_file)
        main_layout.addWidget(self.load_button)

        self.grid_layout = QGridLayout()

        self.pdf_labels = [QLabel("Page {} will be displayed here".format(i + 1)) for i in range(4)]
        for label in self.pdf_labels:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 1px solid black;")  # visual boundary

        # labels
        self.grid_layout.addWidget(self.pdf_labels[0], 0, 0)
        self.grid_layout.addWidget(self.pdf_labels[1], 0, 1)
        self.grid_layout.addWidget(self.pdf_labels[2], 1, 0)
        self.grid_layout.addWidget(self.pdf_labels[3], 1, 1)

        # scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.grid_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # pagination buttons
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.show_previous_pages)
        self.next_button.clicked.connect(self.show_next_pages)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)

        self.setLayout(main_layout)

    def load_hwi_file(self):
        hwi_file, _ = QFileDialog.getOpenFileName(self, "Open .HWI File", "", "HWI Files (*.hwi)")
        if hwi_file:
            extracted_pdf = self.extract_hwi(hwi_file)
            if extracted_pdf:
                self.doc = fitz.open(extracted_pdf)
                self.current_page = 0
                self.display_pdf_pages()
                self.update_pagination_buttons()

    def extract_hwi(self, hwi_path):
        # hwi is a zip file
        with zipfile.ZipFile(hwi_path, 'r') as hwi:
            pdf_files = [f for f in hwi.namelist() if f.endswith('.pdf')]
            if pdf_files:
                extracted_pdf_path = hwi.extract(pdf_files[0], path="temp_extracted")
                return extracted_pdf_path
            else:
                for label in self.pdf_labels:
                    label.setText("No PDF found in the HWI file.")
                return None

    def display_pdf_pages(self):
        if self.doc:
            for i in range(4):
                page_index = self.current_page + i
                if page_index < len(self.doc):
                    page = self.doc.load_page(page_index)
                    pix = page.get_pixmap()
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(img)
                    self.pdf_labels[i].setPixmap(pixmap.scaled(self.pdf_labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.pdf_labels[i].clear()
                    self.pdf_labels[i].setText(f"Page {page_index + 1} does not exist.")

    def show_previous_pages(self):
        if self.current_page >= 4:
            self.current_page -= 4
            self.display_pdf_pages()
            self.update_pagination_buttons()

    def show_next_pages(self):
        if self.current_page + 4 < len(self.doc):
            self.current_page += 4
            self.display_pdf_pages()
            self.update_pagination_buttons()

    def update_pagination_buttons(self):
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page + 4 < len(self.doc))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = AcrobatReader()
    reader.show()
    sys.exit(app.exec())
