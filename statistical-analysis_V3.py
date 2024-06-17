import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, kurtosis

# Generating a random dataset
data = np.random.normal(loc=0, scale=1, size=1000)  # Normal distribution, mean=0, std=1, 1000 samples

# Basic statistics
mean = np.mean(data)
std_dev = np.std(data)
kurt = kurtosis(data)

# Create a figure and a grid of subplots
fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# Bell curve with a histogram on the first subplot
count, bins, ignored = axs[0].hist(data, 30, density=True, alpha=0.5, color='g', edgecolor='black')
# Fit a normal distribution
pdf = norm.pdf(bins, mean, std_dev)
axs[0].plot(bins, pdf, linewidth=2, color='r')
axs[0].set_title('Histogram with Fitted Bell Curve')
axs[0].set_xlabel('Data points')
axs[0].set_ylabel('Probability density')
axs[0].grid(True)

# Adding text box for displaying statistics
textstr = '\n'.join((
    f"Mean: {mean:.2f}",
    f"Standard Deviation: {std_dev:.2f}",
    f"Kurtosis: {kurt:.2f}"))
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
axs[0].text(0.05, 0.95, textstr, transform=axs[0].transAxes, fontsize=12,
            verticalalignment='top', bbox=props)

# Scatter plot on the second subplot
means = [np.mean(np.random.normal(0, 1, 100)) for _ in range(50)]
x = np.arange(len(means))

# Define control and abort limits
control_limit_upper = mean + 2*std_dev
control_limit_lower = mean - 2*std_dev
abort_limit_upper = mean + 3*std_dev
abort_limit_lower = mean - 3*std_dev

axs[1].plot(x, means, 'o', color='b')  # Scatter plot of means
axs[1].axhline(y=control_limit_upper, color='orange', linestyle='--', label='Control Limit Upper')
axs[1].axhline(y=control_limit_lower, color='orange', linestyle='--', label='Control Limit Lower')
axs[1].axhline(y=abort_limit_upper, color='red', linestyle='-', label='Abort Limit Upper')
axs[1].axhline(y=abort_limit_lower, color='red', linestyle='-', label='Abort Limit Lower')
axs[1].set_title('Scatter Plot with Limits')
axs[1].set_xlabel('Sample index')
axs[1].set_ylabel('Mean value')
axs[1].legend()
axs[1].grid(True)

# Show all plots
plt.tight_layout()
plt.show()
