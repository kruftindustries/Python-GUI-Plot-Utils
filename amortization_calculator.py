import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QLabel, QLineEdit, QPushButton, QTableView,
                               QComboBox, QHeaderView, QTableWidgetItem, QTableWidget, QHBoxLayout)
from PySide6.QtCore import Qt
from datetime import datetime

class AmortizationCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Amortized Payment Calculator')
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Loan amount input
        self.loan_amount_label = QLabel('Loan Amount:')
        self.loan_amount_input = QLineEdit()
        layout.addWidget(self.loan_amount_label)
        layout.addWidget(self.loan_amount_input)

        # Interest rate input
        self.interest_rate_label = QLabel('Interest Rate (% per annum):')
        self.interest_rate_input = QLineEdit()
        layout.addWidget(self.interest_rate_label)
        layout.addWidget(self.interest_rate_input)

        # Monthly payment input
        self.monthly_payment_label = QLabel('Monthly Payment:')
        self.monthly_payment_input = QLineEdit()
        layout.addWidget(self.monthly_payment_label)
        layout.addWidget(self.monthly_payment_input)

        # Loan start date input
        self.loan_start_date_label = QLabel('Loan Start Date:')
        loan_start_date_layout = QHBoxLayout()
        self.loan_start_month = QComboBox()
        self.loan_start_year = QComboBox()
        self.populate_date_dropdowns(self.loan_start_month, self.loan_start_year)
        loan_start_date_layout.addWidget(self.loan_start_month)
        loan_start_date_layout.addWidget(self.loan_start_year)
        layout.addWidget(self.loan_start_date_label)
        layout.addLayout(loan_start_date_layout)

        # Additional payment amount input
        self.additional_payment_label = QLabel('Additional Payment:')
        self.additional_payment_input = QLineEdit()
        layout.addWidget(self.additional_payment_label)
        layout.addWidget(self.additional_payment_input)

        # Additional payment date input
        self.additional_payment_date_label = QLabel('Additional Payment Date:')
        additional_payment_date_layout = QHBoxLayout()
        self.additional_payment_month = QComboBox()
        self.additional_payment_year = QComboBox()
        self.populate_date_dropdowns(self.additional_payment_month, self.additional_payment_year)
        additional_payment_date_layout.addWidget(self.additional_payment_month)
        additional_payment_date_layout.addWidget(self.additional_payment_year)
        layout.addWidget(self.additional_payment_date_label)
        layout.addLayout(additional_payment_date_layout)

        # Calculate button
        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate_amortization)
        layout.addWidget(self.calculate_button)

        # Table for displaying the results
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Month', 'Payment', 'Interest', 'Principal', 'Balance'])
        layout.addWidget(self.table)

        self.setCentralWidget(widget)

    def populate_date_dropdowns(self, month_combo, year_combo):
        months = [f"{i:02d}" for i in range(1, 13)]
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year, current_year + 31)]

        month_combo.addItems(months)
        year_combo.addItems(years)

    def calculate_amortization(self):
        # Clear previous results
        self.table.setRowCount(0)

        # Input values
        loan_amount = float(self.loan_amount_input.text())
        interest_rate = float(self.interest_rate_input.text()) / 100 / 12
        monthly_payment = float(self.monthly_payment_input.text())
        additional_payment = float(self.additional_payment_input.text())
        loan_start_date = datetime(int(self.loan_start_year.currentText()), int(self.loan_start_month.currentText()), 1)
        additional_payment_date = datetime(int(self.additional_payment_year.currentText()), int(self.additional_payment_month.currentText()), 1)

        balance = loan_amount
        month = 0
        total_payment = 0
        total_interest = 0
        total_principal = 0

        balance_no_additional = loan_amount
        total_payment_no_additional = 0
        total_interest_no_additional = 0
        total_principal_no_additional = 0

        while balance > 0 or balance_no_additional > 0:
            month += 1
            interest = balance * interest_rate
            principal = monthly_payment - interest
            payment = monthly_payment

            interest_no_additional = balance_no_additional * interest_rate
            principal_no_additional = monthly_payment - interest_no_additional

            # Apply additional payment directly to principal on the specified date
            current_date = loan_start_date.replace(month=(loan_start_date.month + month - 1) % 12 + 1,
                                                   year=loan_start_date.year + (loan_start_date.month + month - 1) // 12)

            if current_date.year == additional_payment_date.year and current_date.month == additional_payment_date.month:
                principal += additional_payment
                payment += additional_payment

            # If the balance is less than the monthly payment, pay the remaining balance and interest
            if balance <= principal:
                principal = balance
                payment = principal + interest
                balance = 0
            else:
                balance -= principal

            # Similarly, handle the no additional payment scenario
            if balance_no_additional <= principal_no_additional:
                principal_no_additional = balance_no_additional
                balance_no_additional = 0
            else:
                balance_no_additional -= principal_no_additional

            # Update totals with and without additional payment
            total_payment += payment
            total_interest += interest
            total_principal += principal

            total_payment_no_additional += principal_no_additional + interest_no_additional
            total_interest_no_additional += interest_no_additional
            total_principal_no_additional += principal_no_additional

            # Add data to table for the scenario with additional payment
            self.table.insertRow(month - 1)
            self.table.setItem(month - 1, 0, QTableWidgetItem(str(month)))
            self.table.setItem(month - 1, 1, QTableWidgetItem(f"{payment:.2f}"))
            self.table.setItem(month - 1, 2, QTableWidgetItem(f"{interest:.2f}"))
            self.table.setItem(month - 1, 3, QTableWidgetItem(f"{principal:.2f}"))
            self.table.setItem(month - 1, 4, QTableWidgetItem(f"{balance:.2f}"))

            # Check if loan is paid off in both scenarios
            if balance == 0 and balance_no_additional == 0:
                break

        # Add totals row with additional payment
        totals_row = self.table.rowCount()
        self.table.insertRow(totals_row)
        self.table.setItem(totals_row, 0, QTableWidgetItem('Totals'))
        self.table.setItem(totals_row, 1, QTableWidgetItem(f"{total_payment:.2f}"))
        self.table.setItem(totals_row, 2, QTableWidgetItem(f"{total_interest:.2f}"))
        self.table.setItem(totals_row, 3, QTableWidgetItem(f"{total_principal:.2f}"))
        self.table.setItem(totals_row, 4, QTableWidgetItem(''))

        # Add totals row without additional payment
        totals_row_no_additional = self.table.rowCount()
        self.table.insertRow(totals_row_no_additional)
        self.table.setItem(totals_row_no_additional, 0, QTableWidgetItem('Totals (No Additional Payment)'))
        self.table.setItem(totals_row_no_additional, 1, QTableWidgetItem(f"{total_payment_no_additional:.2f}"))
        self.table.setItem(totals_row_no_additional, 2, QTableWidgetItem(f"{total_interest_no_additional:.2f}"))
        self.table.setItem(totals_row_no_additional, 3, QTableWidgetItem(f"{total_principal_no_additional:.2f}"))
        self.table.setItem(totals_row_no_additional, 4, QTableWidgetItem(''))

        # Adjust columns to fit content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = AmortizationCalculator()
    window.show()
    sys.exit(app.exec())
