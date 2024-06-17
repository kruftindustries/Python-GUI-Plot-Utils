import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

def create_data(n_samples=300, n_features=2, centers=4, cluster_std=1.0):
    """ Generate random data with specified characteristics. """
    data, _ = make_blobs(n_samples=n_samples, n_features=n_features, centers=centers, cluster_std=cluster_std)
    return data

def apply_kmeans(data, n_clusters=4):
    """ Apply k-means clustering algorithm on the data. """
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(data)
    return kmeans.labels_, kmeans.cluster_centers_

def plot_clusters(data, labels, centers):
    """ Plot the clusters with different colors and the centroids. """
    plt.figure(figsize=(10, 6))
    plt.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=50, alpha=0.6)
    plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.9, marker='x')  # Centroids
    plt.title('Cluster Visualization')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.show()

def main():
    data = create_data(n_samples=300, centers=4)
    labels, centers = apply_kmeans(data, n_clusters=4)
    plot_clusters(data, labels, centers)

if __name__ == "__main__":
    main()
