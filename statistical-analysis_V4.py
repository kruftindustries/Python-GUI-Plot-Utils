import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Function to generate sample data (replace with your actual data)
def generate_data(n=100, mean=50, std=10):
  return np.random.normal(mean, std, n)

# Generate sample data
data = generate_data()

# Calculate statistics
mean = np.mean(data)
std_dev = np.std(data)
kurtosis = stats.kurtosis(data)

# Calculate control limits (assuming 3-sigma limits)
upper_control_limit = mean + 3 * std_dev
lower_control_limit = mean - 3 * std_dev

# Create pandas DataFrame
df = pd.DataFrame({'Value': data})

# Plot 1: Bell Curve with Bar Chart (same as before)
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.hist(data, bins=20, edgecolor='black', density=True)
plt.title("Data Distribution with Bell Curve")
plt.xlabel("Value")
plt.ylabel("Frequency")

# Overlay a normal distribution curve
x = np.linspace(min(data), max(data), 100)
y = stats.norm.pdf(x, mean, std_dev)
plt.plot(x, y, 'r-', label='Normal Distribution')
plt.legend()

# Plot 2: Scatter Plot with Control Limits
plt.subplot(1, 2, 2)
plt.scatter(df.index, df['Value'], marker='o')
plt.axhline(upper_control_limit, color='r', linestyle='--', label='UCL')
plt.axhline(lower_control_limit, color='r', linestyle='--', label='LCL')
plt.title("Scatter Plot with Control Limits")
plt.xlabel("Index")
plt.ylabel("Value")
plt.legend()

# Print summary statistics
print("Dataset Summary:")
print(f"Mean: {mean:.2f}")
print(f"Standard Deviation: {std_dev:.2f}")
print(f"Kurtosis: {kurtosis:.2f}")

plt.tight_layout()
plt.show()