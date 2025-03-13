import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
                             QPushButton, QGroupBox, QSpinBox, QDoubleSpinBox,
                             QComboBox, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DividendCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reverse Dividend Calculator")
        self.setMinimumSize(600, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create input form
        input_group = QGroupBox("Input Parameters")
        form_layout = QFormLayout()
        
        # Create input fields
        self.desired_dividend = QDoubleSpinBox()
        self.desired_dividend.setRange(0, 1000000)
        self.desired_dividend.setPrefix("$ ")
        self.desired_dividend.setDecimals(2)
        self.desired_dividend.setValue(10000)
        
        # Dividend input type selection
        self.dividend_type = QComboBox()
        self.dividend_type.addItems(["Dividend Yield (%)", "Per-Share Dividend"])
        self.dividend_type.currentIndexChanged.connect(self.toggle_dividend_input)
        
        # Stacked widget for different dividend input types
        self.dividend_input_stack = QStackedWidget()
        
        # Option 1: Dividend Yield
        yield_widget = QWidget()
        yield_layout = QHBoxLayout(yield_widget)
        self.dividend_yield = QDoubleSpinBox()
        self.dividend_yield.setRange(0, 100)
        self.dividend_yield.setSuffix(" %")
        self.dividend_yield.setDecimals(2)
        self.dividend_yield.setValue(3.5)
        yield_layout.addWidget(self.dividend_yield)
        yield_layout.setContentsMargins(0, 0, 0, 0)
        
        # Option 2: Per-Share Dividend with Share Price
        per_share_widget = QWidget()
        per_share_layout = QHBoxLayout(per_share_widget)
        
        per_share_form = QFormLayout()
        
        self.per_share_dividend = QDoubleSpinBox()
        self.per_share_dividend.setRange(0, 1000)
        self.per_share_dividend.setPrefix("$ ")
        self.per_share_dividend.setDecimals(3)
        self.per_share_dividend.setValue(1.0)
        
        self.share_price = QDoubleSpinBox()
        self.share_price.setRange(0.01, 100000)
        self.share_price.setPrefix("$ ")
        self.share_price.setDecimals(2)
        self.share_price.setValue(28.57)  # Default to give ~3.5% yield
        
        per_share_form.addRow("Per-Share Dividend:", self.per_share_dividend)
        per_share_form.addRow("Share Price:", self.share_price)
        
        per_share_layout.addLayout(per_share_form)
        per_share_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect signals to update calculations when values change
        self.per_share_dividend.valueChanged.connect(self.update_implied_yield)
        self.share_price.valueChanged.connect(self.update_implied_yield)
        
        # Add widgets to stack
        self.dividend_input_stack.addWidget(yield_widget)
        self.dividend_input_stack.addWidget(per_share_widget)
        
        # Add implied yield label for the per-share option
        self.implied_yield_label = QLabel("(Implied Yield: 3.50%)")
        
        # Create a widget to hold both the stack and the implied yield label
        dividend_container = QWidget()
        dividend_container_layout = QVBoxLayout(dividend_container)
        dividend_container_layout.addWidget(self.dividend_input_stack)
        dividend_container_layout.addWidget(self.implied_yield_label)
        dividend_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initially update the implied yield
        self.update_implied_yield()
        
        self.price_growth = QDoubleSpinBox()
        self.price_growth.setRange(-50, 100)
        self.price_growth.setSuffix(" %")
        self.price_growth.setDecimals(2)
        self.price_growth.setValue(5)
        
        self.holding_period = QSpinBox()
        self.holding_period.setRange(1, 100)
        self.holding_period.setSuffix(" years")
        self.holding_period.setValue(10)
        
        self.cap_gains_rate = QDoubleSpinBox()
        self.cap_gains_rate.setRange(0, 100)
        self.cap_gains_rate.setSuffix(" %")
        self.cap_gains_rate.setDecimals(2)
        self.cap_gains_rate.setValue(20)
        
        self.dividend_tax_rate = QDoubleSpinBox()
        self.dividend_tax_rate.setRange(0, 100)
        self.dividend_tax_rate.setSuffix(" %")
        self.dividend_tax_rate.setDecimals(2)
        self.dividend_tax_rate.setValue(15)
        
        # Add fields to form
        form_layout.addRow("Desired Annual Dividend ($):", self.desired_dividend)
        form_layout.addRow("Dividend Input Type:", self.dividend_type)
        form_layout.addRow("Dividend Details:", dividend_container)
        form_layout.addRow("Expected Annual Price Growth (%):", self.price_growth)
        form_layout.addRow("Holding Period:", self.holding_period)
        form_layout.addRow("Capital Gains Tax Rate (%):", self.cap_gains_rate)
        form_layout.addRow("Dividend Tax Rate (%):", self.dividend_tax_rate)
        
        # Set form layout for input group
        input_group.setLayout(form_layout)
        main_layout.addWidget(input_group)
        
        # Create calculate button
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)
        main_layout.addWidget(calculate_button)
        
        # Create results section
        results_group = QGroupBox("Results")
        results_layout = QFormLayout()
        
        # Create result fields
        self.required_investment = QLabel("$ 0.00")
        self.required_investment.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Investment growth results
        self.ending_investment_value = QLabel("$ 0.00")
        self.investment_growth_percent = QLabel("0.00 %")
        self.capital_gains_tax = QLabel("$ 0.00")
        
        # Dividend results
        self.total_dividends = QLabel("$ 0.00")
        self.dividends_percent = QLabel("0.00 %")
        self.dividend_tax = QLabel("$ 0.00")
        
        # Combined results
        self.ending_balance_after_tax = QLabel("$ 0.00")
        self.cumulative_return_before_tax = QLabel("0.00 %")
        self.cumulative_return_after_tax = QLabel("0.00 %")
        self.total_tax_due = QLabel("$ 0.00")
        
        # Add results to form
        results_layout.addRow("Required Investment:", self.required_investment)
        
        # Investment section
        investment_label = QLabel("Investment Growth:")
        investment_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_layout.addRow(investment_label)
        results_layout.addRow("    Ending Investment Value (Before Tax):", self.ending_investment_value)
        results_layout.addRow("    Investment Growth (%):", self.investment_growth_percent)
        results_layout.addRow("    Capital Gains Tax:", self.capital_gains_tax)
        
        # Dividend section
        dividend_label = QLabel("Dividend Income:")
        dividend_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_layout.addRow(dividend_label)
        results_layout.addRow("    Total Dividends Received:", self.total_dividends)
        results_layout.addRow("    Return from Dividends (%):", self.dividends_percent)
        results_layout.addRow("    Dividend Tax:", self.dividend_tax)
        
        # Combined section
        combined_label = QLabel("Combined Results:")
        combined_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_layout.addRow(combined_label)
        results_layout.addRow("    Cumulative Return (Before Tax):", self.cumulative_return_before_tax)
        results_layout.addRow("    Ending Balance (After Tax):", self.ending_balance_after_tax)
        results_layout.addRow("    Cumulative Return (After Tax):", self.cumulative_return_after_tax)
        results_layout.addRow("    Total Tax Due:", self.total_tax_due)
        
        # Set results layout
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # Add explanation
        explanation = QLabel(
            "This calculator determines the initial investment needed to achieve "
            "your desired annual dividend income based on the specified dividend yield. "
            "It also projects future returns considering price growth and taxes."
        )
        explanation.setWordWrap(True)
        main_layout.addWidget(explanation)
        
    def toggle_dividend_input(self, index):
        """Toggle between dividend yield and per-share dividend input types."""
        self.dividend_input_stack.setCurrentIndex(index)
        self.implied_yield_label.setVisible(index == 1)  # Only show for per-share option
        
    def update_implied_yield(self):
        """Update the implied yield label based on per-share dividend and price."""
        per_share = self.per_share_dividend.value()
        price = self.share_price.value()
        
        if price > 0:
            implied_yield = (per_share / price) * 100
            self.implied_yield_label.setText(f"(Implied Yield: {implied_yield:.2f}%)")
        else:
            self.implied_yield_label.setText("(Invalid share price)")
    
    def calculate(self):
        # Get input values
        desired_dividend = self.desired_dividend.value()
        
        # Get dividend yield depending on selected input type
        if self.dividend_type.currentIndex() == 0:
            # Using direct yield percentage
            dividend_yield = self.dividend_yield.value() / 100
        else:
            # Using per-share dividend and share price
            per_share_dividend = self.per_share_dividend.value()
            share_price = self.share_price.value()
            
            if share_price <= 0:
                self.required_investment.setText("Invalid share price")
                return
                
            dividend_yield = per_share_dividend / share_price
        
        price_growth = self.price_growth.value() / 100
        holding_period = self.holding_period.value()
        cap_gains_rate = self.cap_gains_rate.value() / 100
        dividend_tax_rate = self.dividend_tax_rate.value() / 100
        
        # Calculate required investment to generate desired dividend
        if dividend_yield <= 0:
            self.required_investment.setText("Invalid dividend yield")
            return
            
        required_investment = desired_dividend / dividend_yield
        
        # Calculate ending value before tax
        ending_value_before_tax = required_investment * ((1 + price_growth) ** holding_period)
        
        # Calculate total dividends received
        total_dividends = 0
        for year in range(1, holding_period + 1):
            # Dividends are based on the original investment amount
            # This is a simplification - in reality, dividend amounts would likely change
            total_dividends += desired_dividend
        
        # Calculate tax on dividends
        dividend_tax = total_dividends * dividend_tax_rate
        
        # Calculate capital gains tax
        capital_gain = ending_value_before_tax - required_investment
        capital_gains_tax = capital_gain * cap_gains_rate
        
        # Calculate total tax
        total_tax = dividend_tax + capital_gains_tax
        
        # Calculate ending value after tax
        ending_value_after_tax = ending_value_before_tax - capital_gains_tax
        
        # Calculate returns
        # Before tax: include capital appreciation and all dividends
        cumulative_return_before_tax = ((ending_value_before_tax + total_dividends - required_investment) / required_investment) * 100
        
        # After tax: account for capital gains tax and dividend tax
        cumulative_return_after_tax = ((ending_value_after_tax + (total_dividends * (1 - dividend_tax_rate)) - required_investment) / required_investment) * 100
        
        # Calculate investment growth percentage
        investment_growth_percent = ((ending_value_before_tax - required_investment) / required_investment) * 100
        
        # Calculate dividend return percentage
        dividends_percent = (total_dividends / required_investment) * 100
        
        # Update result fields - Investment section
        self.required_investment.setText(f"$ {required_investment:,.2f}")
        self.ending_investment_value.setText(f"$ {ending_value_before_tax:,.2f}")
        self.investment_growth_percent.setText(f"{investment_growth_percent:.2f} %")
        self.capital_gains_tax.setText(f"$ {capital_gains_tax:,.2f}")
        
        # Update result fields - Dividend section
        self.total_dividends.setText(f"$ {total_dividends:,.2f}")
        self.dividends_percent.setText(f"{dividends_percent:.2f} %")
        self.dividend_tax.setText(f"$ {dividend_tax:,.2f}")
        
        # Update result fields - Combined section
        self.cumulative_return_before_tax.setText(f"{cumulative_return_before_tax:.2f} %")
        self.ending_balance_after_tax.setText(f"$ {ending_value_after_tax:,.2f}")
        self.cumulative_return_after_tax.setText(f"{cumulative_return_after_tax:.2f} %")
        self.total_tax_due.setText(f"$ {total_tax:,.2f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DividendCalculator()
    window.show()
    sys.exit(app.exec())
