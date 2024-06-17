try:
    __import__('PySide6')
    __import__('matplotlib')
except ImportError as e:
    print(f"Please install the missing package: {e.name}")

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QTableView, QLineEdit, QHBoxLayout,
    QMessageBox, QFormLayout
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib
import sys

matplotlib.use('Qt5Agg')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Measurement Uncertainty and Distribution Plotter")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Measurement', 'Accurate Value'])
        self.table_view.setModel(self.model)

        self.add_button = QPushButton("Add Measurement")
        self.add_button.clicked.connect(self.add_measurement)

        self.measurement_input = QLineEdit()
        self.accurate_value_input = QLineEdit()
        
        form_layout = QFormLayout()
        form_layout.addRow("Measurement:", self.measurement_input)
        form_layout.addRow("Accurate Value:", self.accurate_value_input)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.clicked.connect(self.plot_data)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)
        layout.addWidget(self.table_view)
        layout.addWidget(self.plot_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def add_measurement(self):
        measurement_text = self.measurement_input.text()
        accurate_value_text = self.accurate_value_input.text()

        if not measurement_text or not accurate_value_text:
            QMessageBox.warning(self, "Input Error", "Both fields must be filled")
            return

        try:
            measurement = float(measurement_text)
            accurate_value = float(accurate_value_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid input. Please enter numeric values.")
            return

        self.model.appendRow([
            QStandardItem(measurement_text),
            QStandardItem(accurate_value_text)
        ])

        self.measurement_input.clear()
        self.accurate_value_input.clear()
    
    def plot_data(self):
        measurements = []
        accurate_values = []

        for row in range(self.model.rowCount()):
            try:
                measurement = float(self.model.item(row, 0).text())
                accurate_value = float(self.model.item(row, 1).text())
                measurements.append(measurement)
                accurate_values.append(accurate_value)
            except ValueError:
                QMessageBox.warning(self, "Input Error", f"Invalid data at row {row+1}")
                return

        if not measurements or not accurate_values:
            QMessageBox.warning(self, "Input Error", "No data to plot")
            return

        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

        # Candlestick plot
        ax[0].boxplot(measurements, vert=True, patch_artist=True)
        ax[0].set_title('Candlestick Plot of Measurements')
        ax[0].set_ylabel('Measurements')

        # Violin plot
        parts = ax[1].violinplot(measurements, showmeans=False, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('lightblue')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)
        
        ax[1].set_title('Violin Plot of Measurements')
        ax[1].set_ylabel('Measurements')

        plt.tight_layout()
        plt.show()

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MainWindow()
window.show()
sys.exit(app.exec())
