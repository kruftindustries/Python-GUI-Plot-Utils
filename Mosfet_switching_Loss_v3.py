import sys
import csv
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTabWidget, QPushButton, QFileDialog, QLabel,
                             QHBoxLayout, QSpinBox, QSlider, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPen, QColor, QPixmap, QPainter
import xlsxwriter
from datetime import datetime

class CursorControls(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        layout = QHBoxLayout()
        
        # Vertical cursor controls
        vcursor_group = QGroupBox("Vertical Cursors")
        vcursor_layout = QFormLayout()
        self.vcursor1 = QDoubleSpinBox()
        self.vcursor2 = QDoubleSpinBox()
        vcursor_layout.addRow("V1:", self.vcursor1)
        vcursor_layout.addRow("V2:", self.vcursor2)
        vcursor_group.setLayout(vcursor_layout)
        
        # Horizontal cursor controls
        hcursor_group = QGroupBox("Horizontal Cursors")
        hcursor_layout = QFormLayout()
        self.hcursor1 = QDoubleSpinBox()
        self.hcursor2 = QDoubleSpinBox()
        hcursor_layout.addRow("H1:", self.hcursor1)
        hcursor_layout.addRow("H2:", self.hcursor2)
        hcursor_group.setLayout(hcursor_layout)
        
        layout.addWidget(vcursor_group)
        layout.addWidget(hcursor_group)
        self.setLayout(layout)

class AnalysisControls(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        
        # Time range controls
        self.start_time = QDoubleSpinBox()
        self.end_time = QDoubleSpinBox()
        self.start_time.setRange(-999999, 999999)
        self.end_time.setRange(-999999, 999999)
        self.start_time.setDecimals(9)
        self.end_time.setDecimals(9)
        
        # Threshold controls
        self.high_threshold = QSpinBox()
        self.low_threshold = QSpinBox()
        self.high_threshold.setRange(0, 100)
        self.low_threshold.setRange(0, 100)
        self.high_threshold.setValue(90)
        self.low_threshold.setValue(10)
        
        # Auto calculate checkbox
        self.auto_calculate = QCheckBox("Auto Calculate")
        self.auto_calculate.setChecked(True)
        
        # Add widgets to layout
        self.layout.addRow("Start Time (s):", self.start_time)
        self.layout.addRow("End Time (s):", self.end_time)
        self.layout.addRow("High Threshold (%):", self.high_threshold)
        self.layout.addRow("Low Threshold (%):", self.low_threshold)
        self.layout.addRow(self.auto_calculate)


class SwitchingAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Switching Loss Analysis")
        self.setGeometry(100, 100, 1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Data")
        self.export_button = QPushButton("Export Data")
        self.load_button.clicked.connect(self.load_data)
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Initialize charts
        self.turn_off_chart = self.create_chart("Turn-off Transient")
        self.turn_on_chart = self.create_chart("Turn-on Transient")
        self.reverse_recovery_chart = self.create_chart("Reverse Recovery")
        self.vgs_transient_chart = self.create_chart("VGS Transient")
        
        # Create chart views
        self.turn_off_view = QChartView(self.turn_off_chart)
        self.turn_on_view = QChartView(self.turn_on_chart)
        self.reverse_recovery_view = QChartView(self.reverse_recovery_chart)
        self.vgs_transient_view = QChartView(self.vgs_transient_chart)
        
        # Enable chart interaction
        for view in [self.turn_off_view, self.turn_on_view, 
                    self.reverse_recovery_view, self.vgs_transient_view]:
            view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
            view.setInteractive(True)
        
        # Create tabs
        self.turn_off_tab = QWidget()
        self.turn_on_tab = QWidget()
        self.reverse_recovery_tab = QWidget()
        self.vgs_transient_tab = QWidget()

        # Initialize control attributes
        self.turn_off_controls = self.create_tab_controls(self.turn_off_tab, self.turn_off_view, "Turn-off")
        self.turn_on_controls = self.create_tab_controls(self.turn_on_tab, self.turn_on_view, "Turn-on")
        self.reverse_recovery_controls = self.create_tab_controls(self.reverse_recovery_tab, self.reverse_recovery_view, "Reverse Recovery")
        self.vgs_transient_controls = self.create_tab_controls(self.vgs_transient_tab, self.vgs_transient_view, "VGS Transient")
        
        # Add tabs
        self.tabs.addTab(self.turn_off_tab, "Turn-off Transient")
        self.tabs.addTab(self.turn_on_tab, "Turn-on Transient")
        self.tabs.addTab(self.reverse_recovery_tab, "Reverse Recovery")
        self.tabs.addTab(self.vgs_transient_tab, "VGS Transient")
        
        self.data = None

    def create_tab_controls(self, tab, chart_view, name):
        layout = QVBoxLayout(tab)
        
        # Add chart view
        layout.addWidget(chart_view)
        
        # Create bottom control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Time range group
        time_group = QGroupBox("Time Range")
        time_layout = QHBoxLayout()
        
        # Start time controls
        start_layout = QVBoxLayout()
        start_label = QLabel("Start Time:")
        start_time = QDoubleSpinBox()
        start_time.setRange(-999999, 999999)
        start_time.setDecimals(9)
        start_time.setSingleStep(1e-9)
        start_layout.addWidget(start_label)
        start_layout.addWidget(start_time)
        
        # End time controls
        end_layout = QVBoxLayout()
        end_label = QLabel("End Time:")
        end_time = QDoubleSpinBox()
        end_time.setRange(-999999, 999999)
        end_time.setDecimals(9)
        end_time.setSingleStep(1e-9)
        end_layout.addWidget(end_label)
        end_layout.addWidget(end_time)
        
        # Time range buttons
        button_layout = QVBoxLayout()
        auto_range = QPushButton("Auto Range")
        apply_range = QPushButton("Apply")
        reset_range = QPushButton("Reset")
        auto_calculate = QCheckBox("Auto Calculate")  # Add auto calculate checkbox
        auto_calculate.setChecked(True)
        button_layout.addWidget(auto_range)
        button_layout.addWidget(apply_range)
        button_layout.addWidget(reset_range)
        button_layout.addWidget(auto_calculate)  # Add to layout
        
        # Connect signals
        auto_range.clicked.connect(lambda: self.set_auto_range(chart_view))
        apply_range.clicked.connect(lambda: self.apply_time_range(chart_view))
        reset_range.clicked.connect(lambda: self.reset_time_range(chart_view))
        
        # Connect control signals
        start_time.valueChanged.connect(lambda: self.apply_time_range(chart_view))
        end_time.valueChanged.connect(lambda: self.apply_time_range(chart_view))
        auto_calculate.stateChanged.connect(lambda: self.apply_time_range(chart_view))
        
        # Add all layouts to time group
        time_layout.addLayout(start_layout)
        time_layout.addLayout(end_layout)
        time_layout.addLayout(button_layout)
        time_group.setLayout(time_layout)
        
        # Threshold group
        threshold_group = QGroupBox("Thresholds")
        threshold_layout = QHBoxLayout()
        
        # High threshold controls
        high_layout = QVBoxLayout()
        high_label = QLabel("High (%):")
        high_threshold = QSpinBox()
        high_threshold.setRange(0, 100)
        high_threshold.setValue(90)
        high_layout.addWidget(high_label)
        high_layout.addWidget(high_threshold)
        
        # Low threshold controls
        low_layout = QVBoxLayout()
        low_label = QLabel("Low (%):")
        low_threshold = QSpinBox()
        low_threshold.setRange(0, 100)
        low_threshold.setValue(10)
        low_layout.addWidget(low_label)
        low_layout.addWidget(low_threshold)
        
        threshold_layout.addLayout(high_layout)
        threshold_layout.addLayout(low_layout)
        threshold_group.setLayout(threshold_layout)
        
        # Add groups to control panel
        control_layout.addWidget(time_group)
        control_layout.addWidget(threshold_group)
        
        # Add control panel to main layout
        layout.addWidget(control_panel)

        # Create a control object to return
        controls = type('Controls', (), {
            'start_time': start_time,
            'end_time': end_time,
            'high_threshold': high_threshold,
            'low_threshold': low_threshold,
            'auto_range': auto_range,
            'apply_range': apply_range,
            'reset_range': reset_range,
            'auto_calculate': auto_calculate  # Add auto_calculate to controls object
        })
        
        return controls

    def set_auto_range(self, chart_view):
        if self.data:
            # Get the current tab and its controls
            current_tab = self.tabs.currentWidget()
            
            if current_tab == self.turn_off_tab:
                controls = self.turn_off_controls
            elif current_tab == self.turn_on_tab:
                controls = self.turn_on_controls
            elif current_tab == self.reverse_recovery_tab:
                controls = self.reverse_recovery_controls
            elif current_tab == self.vgs_transient_tab:
                controls = self.vgs_transient_controls
            else:
                return

            chart = chart_view.chart()
            axis_x = chart.axes(Qt.Horizontal)[0]
            axis_x.setRange(min(self.data['time']), max(self.data['time']))
            controls.start_time.setValue(min(self.data['time']))
            controls.end_time.setValue(max(self.data['time']))

    def apply_time_range(self, chart_view):
        # Get the current tab and its controls
        current_tab = self.tabs.currentWidget()
        
        if current_tab == self.turn_off_tab:
            controls = self.turn_off_controls
        elif current_tab == self.turn_on_tab:
            controls = self.turn_on_controls
        elif current_tab == self.reverse_recovery_tab:
            controls = self.reverse_recovery_controls
        elif current_tab == self.vgs_transient_tab:
            controls = self.vgs_transient_controls
        else:
            return

        chart = chart_view.chart()
        axis_x = chart.axes(Qt.Horizontal)[0]
        axis_x.setRange(controls.start_time.value(), controls.end_time.value())
        
        # Update the plot with new range
        self.update_plot_range(chart_view, controls.start_time.value(), controls.end_time.value())

    def reset_time_range(self, chart_view):
        if self.data:
            self.set_auto_range(chart_view)
        
    def create_chart(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Set dark theme colors
        chart.setBackgroundBrush(QColor("#2B2B2B"))
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.legend().setLabelColor(QColor("#FFFFFF"))
        
        axis_x = QValueAxis()
        axis_x.setTitleText("Time (s)")
        axis_x.setLabelsColor(QColor("#FFFFFF"))
        axis_x.setTitleBrush(QColor("#FFFFFF"))
        axis_x.setGridLineColor(QColor("#404040"))
        axis_x.setLinePenColor(QColor("#808080"))
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Voltage/Current")
        axis_y.setLabelsColor(QColor("#FFFFFF"))
        axis_y.setTitleBrush(QColor("#FFFFFF"))
        axis_y.setGridLineColor(QColor("#404040"))
        axis_y.setLinePenColor(QColor("#808080"))
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        return chart


    def create_series(self, name, color):
        series = QLineSeries()
        series.setName(name)
        pen = QPen(color)
        pen.setWidth(2)
        series.setPen(pen)
        return series

    def load_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "CSV Files (*.csv)")
        if filename:
            self.load_csv_data(filename)
            self.process_and_plot_data()

    def load_csv_data(self, filename):
        self.data = {
            'time': [], 'vgs': [], 'vds': [], 'is': []
        }
        
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                self.data['time'].append(float(row['Time']))
                self.data['vgs'].append(float(row['Vgs']))
                self.data['vds'].append(float(row['Vds']))
                self.data['is'].append(float(row['Is']))

    def process_and_plot_data(self):
        if not self.data:
            return
        
        self.clear_charts()
        self.plot_turn_off_transient()
        self.plot_turn_on_transient()
        self.plot_reverse_recovery()
        self.plot_vgs_transient()

    def clear_charts(self):
        for chart in [self.turn_off_chart, self.turn_on_chart, 
                     self.reverse_recovery_chart, self.vgs_transient_chart]:
            chart.removeAllSeries()

    def plot_turn_off_transient(self):
        start_idx, end_idx = self.get_analysis_range(self.turn_off_controls)
        #vgs_series = self.create_series("VGS", QColor("#5B9BD5"))  # Light blue
        #vds_series = self.create_series("VDS", QColor("#ED7D31"))  # Orange
        #is_series = self.create_series("IS", QColor("#70AD47"))    # Green
        vgs_series = self.create_series("VGS", QColor(Qt.blue))
        vds_series = self.create_series("VDS", QColor(Qt.red))
        is_series = self.create_series("IS", QColor(Qt.green))
        
        for i in range(start_idx, end_idx + 1):
            vgs_series.append(self.data['time'][i], self.data['vgs'][i])
            vds_series.append(self.data['time'][i], self.data['vds'][i])
            is_series.append(self.data['time'][i], self.data['is'][i])
        
        self.turn_off_chart.addSeries(vgs_series)
        self.turn_off_chart.addSeries(vds_series)
        self.turn_off_chart.addSeries(is_series)
        
        for series in [vgs_series, vds_series, is_series]:
            series.attachAxis(self.turn_off_chart.axes()[0])
            series.attachAxis(self.turn_off_chart.axes()[1])
        
        params = self.calculate_turn_off_params()
        self.add_turn_off_annotations(params)

    def plot_turn_on_transient(self):
        start_idx, end_idx = self.get_analysis_range(self.turn_on_controls)
        #vgs_series = self.create_series("VGS", QColor("#5B9BD5"))  # Light blue
        #vds_series = self.create_series("VDS", QColor("#ED7D31"))  # Orange
        #is_series = self.create_series("IS", QColor("#70AD47"))    # Green
        vgs_series = self.create_series("VGS", QColor(Qt.blue))
        vds_series = self.create_series("VDS", QColor(Qt.red))
        is_series = self.create_series("IS", QColor(Qt.green))
        
        for i in range(start_idx, end_idx + 1):
            vgs_series.append(self.data['time'][i], self.data['vgs'][i])
            vds_series.append(self.data['time'][i], self.data['vds'][i])
            is_series.append(self.data['time'][i], self.data['is'][i])
        
        self.turn_on_chart.addSeries(vgs_series)
        self.turn_on_chart.addSeries(vds_series)
        self.turn_on_chart.addSeries(is_series)
        
        for series in [vgs_series, vds_series, is_series]:
            series.attachAxis(self.turn_on_chart.axes()[0])
            series.attachAxis(self.turn_on_chart.axes()[1])
        
        params = self.calculate_turn_on_params()
        self.add_turn_on_annotations(params)
    
    def plot_reverse_recovery(self):
        start_idx, end_idx = self.get_analysis_range(self.reverse_recovery_controls)
        #current_series = self.create_series("IRR", QColor("#5B9BD5"))  # Light blue
        current_series = self.create_series("IRR", QColor(Qt.blue))
        
        for i in range(start_idx, end_idx + 1):
            current_series.append(self.data['time'][i], self.data['is'][i])
        
        self.reverse_recovery_chart.addSeries(current_series)
        current_series.attachAxis(self.reverse_recovery_chart.axes()[0])
        current_series.attachAxis(self.reverse_recovery_chart.axes()[1])
        
        params = self.calculate_reverse_recovery_params()
        self.add_reverse_recovery_annotations(params)

    def plot_vgs_transient(self):
        start_idx, end_idx = self.get_analysis_range(self.vgs_transient_controls)
        #vgs_series = self.create_series("VGS", QColor("#C586C0"))  # Light purple
        vgs_series = self.create_series("VGS", QColor(Qt.magenta))
        
        for i in range(start_idx, end_idx + 1):
            vgs_series.append(self.data['time'][i], self.data['vgs'][i])
        
        self.vgs_transient_chart.addSeries(vgs_series)
        vgs_series.attachAxis(self.vgs_transient_chart.axes()[0])
        vgs_series.attachAxis(self.vgs_transient_chart.axes()[1])
        
        params = self.calculate_vgs_transient_params()
        self.add_vgs_transient_annotations(params)

    def calculate_turn_off_params(self):
        vgs_max = max(self.data['vgs'])
        vds_max = max(self.data['vds'])
        is_max = max(self.data['is'])
        
        return {
            'vgs_90': vgs_max * 0.9,
            'vds_10': vds_max * 0.1,
            'is_10': is_max * 0.1,
            't_off': self.find_fall_time(self.data['vgs'], 0.9, 0.1),
            'td_off': self.find_delay_time(self.data['vds'], 0.4, 0.6),
            'dv_dt_off': self.calculate_slope(self.data['vds']),
            'di_dt_off': self.calculate_slope(self.data['is']),
            'e_off': self.calculate_energy(self.data['vds'], self.data['is'])
        }

    def calculate_turn_on_params(self):
        vgs_max = max(self.data['vgs'])
        vds_max = max(self.data['vds'])
        is_max = max(self.data['is'])
        
        return {
            'vgs_10': vgs_max * 0.1,
            'vds_90': vds_max * 0.9,
            'is_90': is_max * 0.9,
            't_on': self.find_rise_time(self.data['vgs'], 0.1, 0.9),
            'td_on': self.find_delay_time(self.data['vds'], 0.6, 0.4),
            'dv_dt_on': self.calculate_slope(self.data['vds']),
            'di_dt_on': self.calculate_slope(self.data['is']),
            'e_on': self.calculate_energy(self.data['vds'], self.data['is'])
        }

    def find_fall_time(self, data, high, low):
        # Implementation for fall time calculation
        return 1e-6  # placeholder

    def find_rise_time(self, data, low, high):
        # Implementation for rise time calculation
        return 1e-6  # placeholder

    def find_delay_time(self, data, start, end):
        # Implementation for delay time calculation
        return 1e-6  # placeholder

    def calculate_slope(self, data):
        # Implementation for slope calculation
        return 1e6  # placeholder

    def calculate_energy(self, vds, Is):
        # Implementation for energy calculation
        return 1e-3  # placeholder
        
    def calculate_reverse_recovery_params(self):
        # Find IF (forward current)
        If = max(self.data['is'])
        # Find Irrm (peak reverse recovery current) 
        Irrm = min(self.data['is'])
        
        # Calculate di/dt between 60% and 40% points
        If_Irrm_diff = If - Irrm
        sixty_percent = If - (0.6 * If_Irrm_diff)
        forty_percent = If - (0.4 * If_Irrm_diff)
        
        # Find corresponding times
        t60 = self.find_time_at_value(self.data['is'], sixty_percent)
        t40 = self.find_time_at_value(self.data['is'], forty_percent)
        
        di_dt = (sixty_percent - forty_percent)/(t60 - t40)
        
        # Find trr (reverse recovery time)
        t1 = self.find_time_at_value(self.data['is'], 0, 'falling')
        t2 = self.find_time_at_value(self.data['is'], 0, 'rising')
        trr = t2 - t1
        
        # Calculate tf and ts components
        tf = t1 - self.find_time_at_value(self.data['is'], If)
        ts = t2 - t1
        
        # Calculate Qrr (reverse recovery charge)
        Qrr = self.calculate_area_under_curve(
            self.data['time'], 
            self.data['is'],
            t1,
            t2
        )
        
        return {
            'If': If,
            'Irrm': Irrm,
            'di_dt': di_dt,
            'trr': trr,
            'tf': tf,
            'ts': ts,
            'Qrr': Qrr
        }

    def calculate_vgs_transient_params(self):
        if not self.data or not self.data['vgs']:
            return {'vgs_static': 0, 'vgs_dynamic': 0}

        # Window size for moving average (adjust based on your sampling rate)
        window_size = min(50, len(self.data['vgs']) // 10)
        
        # Calculate moving average to find steady-state levels
        moving_avg = self.calculate_moving_average(self.data['vgs'], window_size)
        
        # Find steady state high and low levels (static)
        static_high = self.find_steady_state_level(moving_avg, 'high')
        static_low = self.find_steady_state_level(moving_avg, 'low')
        vgs_static = static_high - static_low
        
        # Find absolute peak values (dynamic)
        dynamic_high = max(self.data['vgs'])
        dynamic_low = min(self.data['vgs'])
        vgs_dynamic = dynamic_high - dynamic_low
        
        return {
            'vgs_static': vgs_static,
            'vgs_dynamic': vgs_dynamic,
            'static_high': static_high,
            'static_low': static_low,
            'dynamic_high': dynamic_high,
            'dynamic_low': dynamic_low
        }

    def calculate_moving_average(self, data, window_size):
        """Calculate moving average of the signal."""
        moving_avg = []
        for i in range(len(data)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(data), i + window_size // 2)
            window = data[start_idx:end_idx]
            moving_avg.append(sum(window) / len(window))
        return moving_avg

    def find_steady_state_level(self, data, level_type='high'):
        """Find the most common steady-state level using histogram analysis."""
        if not data:
            return 0
            
        # Calculate min and max for bin ranges
        min_val = min(data)
        max_val = max(data)
        
        # Create 100 bins
        num_bins = 100
        bin_width = (max_val - min_val) / num_bins
        bins = [min_val + i * bin_width for i in range(num_bins + 1)]
        
        # Initialize histogram counts
        hist_counts = [0] * num_bins
        
        # Count values in each bin
        for value in data:
            bin_index = min(int((value - min_val) // bin_width), num_bins - 1)
            hist_counts[bin_index] += 1
        
        # Calculate bin centers
        bin_centers = [(bins[i] + bins[i + 1]) / 2 for i in range(num_bins)]
        
        # Calculate mean of data
        data_mean = sum(data) / len(data)
        
        if level_type == 'high':
            # Find the highest voltage that occurs frequently
            max_count = 0
            max_bin_value = 0
            for i in range(num_bins):
                if bin_centers[i] > data_mean:
                    if hist_counts[i] > max_count:
                        max_count = hist_counts[i]
                        max_bin_value = bin_centers[i]
            return max_bin_value
        else:
            # Find the lowest voltage that occurs frequently
            max_count = 0
            min_bin_value = 0
            for i in range(num_bins):
                if bin_centers[i] < data_mean:
                    if hist_counts[i] > max_count:
                        max_count = hist_counts[i]
                        min_bin_value = bin_centers[i]
            return min_bin_value
        
        return 0

    def find_time_at_value(self, data, target, direction='falling'):
        for i in range(len(data)-1):
            if direction == 'falling':
                if data[i] >= target >= data[i+1]:
                    return self.data['time'][i]
            else:
                if data[i] <= target <= data[i+1]:
                    return self.data['time'][i]
        return 0

    def calculate_area_under_curve(self, time, data, t1, t2):
        area = 0
        for i in range(len(time)-1):
            if t1 <= time[i] <= t2:
                dt = time[i+1] - time[i]
                avg_height = (data[i] + data[i+1])/2
                area += avg_height * dt
        return abs(area)

    def add_turn_off_annotations(self, params):
        text = (f"90% VGS: {params['vgs_90']:.2f}V\n"
                f"toff: {params['t_off']:.2e}s\n"
                f"td(off): {params['td_off']:.2e}s\n"
                f"dV/dt_off: {params['dv_dt_off']:.2e}V/s\n"
                f"dI/dt_off: {params['di_dt_off']:.2e}A/s\n"
                f"10% VDS: {params['vds_10']:.2f}V\n"
                f"10% IS: {params['is_10']:.2f}A\n"
                f"Eoff: {params['e_off']:.2e}J")
        
        label = QLabel(text)
        #label.setStyleSheet("background-color: white; padding: 5px; border: 1px solid black")
        label.setStyleSheet("""
            background-color: #2B2B2B;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #808080;
            border-radius: 3px;
        """)
        self.turn_off_chart.scene().addWidget(label)

    def add_turn_on_annotations(self, params):
        text = (f"10% VGS: {params['vgs_10']:.2f}V\n"
                f"ton: {params['t_on']:.2e}s\n"
                f"td(on): {params['td_on']:.2e}s\n"
                f"dV/dt_on: {params['dv_dt_on']:.2e}V/s\n"
                f"dI/dt_on: {params['di_dt_on']:.2e}A/s\n"
                f"90% VDS: {params['vds_90']:.2f}V\n"
                f"90% IS: {params['is_90']:.2f}A\n"
                f"Eon: {params['e_on']:.2e}J")
        
        label = QLabel(text)
        #label.setStyleSheet("background-color: white; padding: 5px; border: 1px solid black")
        label.setStyleSheet("""
            background-color: #2B2B2B;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #808080;
            border-radius: 3px;
        """)
        self.turn_on_chart.scene().addWidget(label)
        
    def add_reverse_recovery_annotations(self, params):
        text = (f"IF: {params['If']:.2f}A\n"
                f"IRRM: {params['Irrm']:.2f}A\n"
                f"dI/dt: {params['di_dt']:.2e}A/s\n"
                f"trr: {params['trr']:.2e}s\n"
                f"tf: {params['tf']:.2e}s\n"
                f"ts: {params['ts']:.2e}s\n"
                f"Qrr: {params['Qrr']:.2e}C")
        
        label = QLabel(text)
        #label.setStyleSheet("background-color: white; padding: 5px; border: 1px solid black")
        label.setStyleSheet("""
            background-color: #2B2B2B;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #808080;
            border-radius: 3px;
        """)
        self.reverse_recovery_chart.scene().addWidget(label)

    def add_vgs_transient_annotations(self, params):
        text = (f"VGS-static: {params['vgs_static']:.2f}V\n"
                f"  High: {params['static_high']:.2f}V\n"
                f"  Low: {params['static_low']:.2f}V\n"
                f"VGS-dynamic: {params['vgs_dynamic']:.2f}V\n"
                f"  Peak High: {params['dynamic_high']:.2f}V\n"
                f"  Peak Low: {params['dynamic_low']:.2f}V")
        
        label = QLabel(text)
        label.setStyleSheet("""
            background-color: #2B2B2B;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #808080;
            border-radius: 3px;
        """)
        self.vgs_transient_chart.scene().addWidget(label)
        
    def update_analysis(self):
        """Update the analysis based on control values"""
        if not self.data:
            return
            
        # Get the current tab
        current_tab = self.tabs.currentWidget()
        
        # Get the corresponding controls
        if current_tab == self.turn_off_tab:
            controls = self.turn_off_controls
            self.plot_turn_off_transient()
        elif current_tab == self.turn_on_tab:
            controls = self.turn_on_controls
            self.plot_turn_on_transient()
        elif current_tab == self.reverse_recovery_tab:
            controls = self.reverse_recovery_controls
            self.plot_reverse_recovery()
        elif current_tab == self.vgs_transient_tab:
            controls = self.vgs_transient_controls
            self.plot_vgs_transient()

    def get_analysis_range(self, controls):
        """Get the data range based on control settings"""
        if not self.data or not self.data['time']:
            return 0, 0
            
        if controls.auto_calculate.isChecked():
            return 0, len(self.data['time']) - 1
            
        start_time = controls.start_time.value()
        end_time = controls.end_time.value()
        
        # Find corresponding indices
        start_idx = 0
        end_idx = len(self.data['time']) - 1
        
        # Find start index
        for i, t in enumerate(self.data['time']):
            if t >= start_time:
                start_idx = i
                break
                
        # Find end index
        for i in range(start_idx, len(self.data['time'])):
            if self.data['time'][i] >= end_time:
                end_idx = i
                break
        
        # Ensure end_idx is not less than start_idx
        end_idx = max(end_idx, start_idx)
        
        return start_idx, end_idx
        
    def update_plot_range(self, chart_view, start_time, end_time):
        if not self.data:
            return
            
        # Find corresponding indices
        start_idx = 0
        end_idx = len(self.data['time']) - 1
        
        for i, t in enumerate(self.data['time']):
            if t >= start_time:
                start_idx = i
                break
                
        for i, t in enumerate(self.data['time'][start_idx:], start_idx):
            if t >= end_time:
                end_idx = i
                break
        
        # Update chart with new range
        chart = chart_view.chart()
        chart.removeAllSeries()
        
        # Create and add new series with range-limited data
        vgs_series = self.create_series("VGS", QColor(Qt.blue))
        vds_series = self.create_series("VDS", QColor(Qt.red))
        is_series = self.create_series("IS", QColor(Qt.green))
        
        for i in range(start_idx, end_idx + 1):
            vgs_series.append(self.data['time'][i], self.data['vgs'][i])
            vds_series.append(self.data['time'][i], self.data['vds'][i])
            is_series.append(self.data['time'][i], self.data['is'][i])
        
        chart.addSeries(vgs_series)
        chart.addSeries(vds_series)
        chart.addSeries(is_series)
        
        # Attach axes
        for series in [vgs_series, vds_series, is_series]:
            series.attachAxis(chart.axes()[0])
            series.attachAxis(chart.axes()[1])

    def update_all_plots(self):
        for view, controls in [
            (self.turn_off_view, self.turn_off_controls),
            (self.turn_on_view, self.turn_on_controls),
            (self.reverse_recovery_view, self.reverse_recovery_controls),
            (self.vgs_transient_view, self.vgs_transient_controls)
        ]:
            self.update_plot_range(view, controls.start_time.value(), controls.end_time.value())

    def export_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "Excel Files (*.xlsx)")
        if filename:
            workbook = xlsxwriter.Workbook(filename)
            
            # Export data and charts for each tab
            self.export_tab_data(workbook, "Turn-off", self.turn_off_view)
            self.export_tab_data(workbook, "Turn-on", self.turn_on_view)
            self.export_tab_data(workbook, "Reverse Recovery", self.reverse_recovery_view)
            self.export_tab_data(workbook, "VGS Transient", self.vgs_transient_view)
            
            workbook.close()

    def export_tab_data(self, workbook, sheet_name, chart_view):
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Get the appropriate controls based on sheet name
        if sheet_name == "Turn-off":
            controls = self.turn_off_controls
        elif sheet_name == "Turn-on":
            controls = self.turn_on_controls
        elif sheet_name == "Reverse Recovery":
            controls = self.reverse_recovery_controls
        elif sheet_name == "VGS Transient":
            controls = self.vgs_transient_controls
        else:
            return

        # Get start and end indices based on time range
        start_idx, end_idx = self.get_analysis_range(controls)
        
        # Add data headers
        headers = ['Time', 'VGS', 'VDS', 'IS']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Write data within the selected range
        if self.data:
            row = 1
            for i in range(start_idx, end_idx + 1):
                worksheet.write(row, 0, self.data['time'][i])
                worksheet.write(row, 1, self.data['vgs'][i])
                worksheet.write(row, 2, self.data['vds'][i])
                worksheet.write(row, 3, self.data['is'][i])
                row += 1
        
        # Create Excel chart
        chart = workbook.add_chart({'type': 'line'})
        
        # Get the number of rows with data in the selected range
        num_rows = end_idx - start_idx + 1
        
        #if (' ' in sheet_name):# add single quote for sheet name with spaces
        sheet_name = "\'" + sheet_name + "\'" # add single quote for all sheet names ion formulas / series
        
        # Add voltage series to primary y-axis
        chart.add_series({
            'name': 'VGS',
            'categories': f'={sheet_name}!$A$2:$A${num_rows+1}',
            'values': f'={sheet_name}!$B$2:$B${num_rows+1}',
            'line': {'color': 'blue', 'width': 1.5},
            'y_axis': 0,  # Primary axis
        })
        
        chart.add_series({
            'name': 'VDS',
            'categories': f'={sheet_name}!$A$2:$A${num_rows+1}',
            'values': f'={sheet_name}!$C$2:$C${num_rows+1}',
            'line': {'color': 'red', 'width': 1.5},
            'y_axis': 0,  # Primary axis
        })
        
        # Add current series to secondary y-axis
        chart.add_series({
            'name': 'IS',
            'categories': f'={sheet_name}!$A$2:$A${num_rows+1}',
            'values': f'={sheet_name}!$D$2:$D${num_rows+1}',
            'line': {'color': 'green', 'width': 1.5},
            'y2_axis': True,  # Secondary axis
        })
        
        # Configure chart
        chart.set_title({'name': sheet_name})
        chart.set_x_axis({
            'name': 'Time (s)',
            'major_gridlines': {'visible': True},
        })
        
        # Configure primary y-axis (voltage)
        chart.set_y_axis({
            'name': 'Voltage (V)',
            'major_gridlines': {'visible': True},
        })
        
        # Configure secondary y-axis (current)
        chart.set_y2_axis({
            'name': 'Current (A)',
            'major_gridlines': {'visible': True},
        })
        
        chart.set_legend({'position': 'bottom'})
        chart.set_size({'width': 720, 'height': 480})
        
        # Insert chart into worksheet
        worksheet.insert_chart('F2', chart)
        
        # Add analysis parameters if available
        if sheet_name == "Turn-off":
            params = self.calculate_turn_off_params()
            row = 2
            worksheet.write(row, 8, "Turn-off Parameters")
            worksheet.write(row+1, 8, f"90% VGS: {params['vgs_90']:.2f} V")
            worksheet.write(row+2, 8, f"toff: {params['t_off']:.2e} s")
            worksheet.write(row+3, 8, f"td(off): {params['td_off']:.2e} s")
            worksheet.write(row+4, 8, f"dV/dt_off: {params['dv_dt_off']:.2e} V/s")
            worksheet.write(row+5, 8, f"dI/dt_off: {params['di_dt_off']:.2e} A/s")
            worksheet.write(row+6, 8, f"10% VDS: {params['vds_10']:.2f} V")
            worksheet.write(row+7, 8, f"10% IS: {params['is_10']:.2f} A")
            worksheet.write(row+8, 8, f"Eoff: {params['e_off']:.2e} J")
        
        elif sheet_name == "Turn-on":
            params = self.calculate_turn_on_params()
            row = 2
            worksheet.write(row, 8, "Turn-on Parameters")
            worksheet.write(row+1, 8, f"10% VGS: {params['vgs_10']:.2f} V")
            worksheet.write(row+2, 8, f"ton: {params['t_on']:.2e} s")
            worksheet.write(row+3, 8, f"td(on): {params['td_on']:.2e} s")
            worksheet.write(row+4, 8, f"dV/dt_on: {params['dv_dt_on']:.2e} V/s")
            worksheet.write(row+5, 8, f"dI/dt_on: {params['di_dt_on']:.2e} A/s")
            worksheet.write(row+6, 8, f"90% VDS: {params['vds_90']:.2f} V")
            worksheet.write(row+7, 8, f"90% IS: {params['is_90']:.2f} A")
            worksheet.write(row+8, 8, f"Eon: {params['e_on']:.2e} J")
        
        elif sheet_name == "Reverse Recovery":
            params = self.calculate_reverse_recovery_params()
            row = 2
            worksheet.write(row, 8, "Reverse Recovery Parameters")
            worksheet.write(row+1, 8, f"IF: {params['If']:.2f} A")
            worksheet.write(row+2, 8, f"IRRM: {params['Irrm']:.2f} A") 
            worksheet.write(row+3, 8, f"dI/dt: {params['di_dt']:.2e} A/s")
            worksheet.write(row+4, 8, f"trr: {params['trr']:.2e} s")
            worksheet.write(row+5, 8, f"tf: {params['tf']:.2e} s")
            worksheet.write(row+6, 8, f"ts: {params['ts']:.2e} s")
            worksheet.write(row+7, 8, f"Qrr: {params['Qrr']:.2e} C")

        elif sheet_name == "VGS Transient":
            params = self.calculate_vgs_transient_params()
            row = 2
            worksheet.write(row, 8, "VGS Transient Parameters")
            worksheet.write(row+1, 8, f"VGS-static: {params['vgs_static']:.2f} V")
            worksheet.write(row+2, 8, f"  Static High: {params['static_high']:.2f} V")
            worksheet.write(row+3, 8, f"  Static Low: {params['static_low']:.2f} V")
            worksheet.write(row+4, 8, f"VGS-dynamic: {params['vgs_dynamic']:.2f} V")
            worksheet.write(row+5, 8, f"  Dynamic High: {params['dynamic_high']:.2f} V")
            worksheet.write(row+6, 8, f"  Dynamic Low: {params['dynamic_low']:.2f} V")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SwitchingAnalysisApp()
    app.setStyle('Fusion')
    window.show()
    sys.exit(app.exec())