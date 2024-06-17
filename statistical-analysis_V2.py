import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, kurtosis

# Generating a random dataset
data = np.random.normal(loc=0, scale=1, size=1000)  # Normal distribution, mean=0, std=1, 1000 samples

# Basic statistics
mean = np.mean(data)
std_dev = np.std(data)
kurt = kurtosis(data)

print(f"Mean: {mean:.2f}")
print(f"Standard Deviation: {std_dev:.2f}")
print(f"Kurtosis: {kurt:.2f}")

# Setting up subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))

# Bell curve with a histogram on the first subplot
count, bins, ignored = ax1.hist(data, 30, density=True, alpha=0.5, color='g', edgecolor='black')
# Fit a normal distribution
pdf = norm.pdf(bins, mean, std_dev)
ax1.plot(bins, pdf, linewidth=2, color='r')
ax1.set_title('Bell Curve with Bar Chart')
ax1.set_xlabel('Data points')
ax1.set_ylabel('Probability density')
ax1.grid(True)

# Scatter plot with horizontal dashed red lines for error bars on the second subplot
means = [np.mean(np.random.normal(0, 1, 100)) for _ in range(50)]
std_devs = [np.std(np.random.normal(0, 1, 100)) for _ in range(50)]
x = np.arange(len(means))

ax2.plot(x, means, 'o', color='b')  # Scatter plot of means
for i in range(len(means)):
    ax2.plot([x[i] - std_devs[i], x[i] + std_devs[i]], [means[i], means[i]], '--r')  # Horizontal dashed red lines for std deviations

ax2.set_title('Scatter Plot with Horizontal Dashed Red Error Bars')
ax2.set_xlabel('Sample index')
ax2.set_ylabel('Mean value')
ax2.grid(True)

# Show all plots
plt.tight_layout()
plt.show()
