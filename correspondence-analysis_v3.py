#python -m pip install prince
import pandas as pd
import prince
import matplotlib.pyplot as plt

def load_data():
    # Sample data creation
    data = {
        'Nationality': ['USA', 'Canada', 'USA', 'Canada', 'USA', 'Canada'],
        'Handedness': ['Right', 'Right', 'Left', 'Right', 'Left', 'Left']
    }
    df = pd.DataFrame(data)

    # Convert to a contingency table
    contingency_table = pd.crosstab(df['Nationality'], df['Handedness'])
    return contingency_table

def perform_correspondence_analysis(data):
    # Initialize the CA object with the 'sklearn' engine
    ca = prince.CA(
        n_components=1,  # Adjusting the number of components to 1 since that's all the data supports
        n_iter=3,        # the number of iterations of the CA algorithm
        copy=True,       # whether to copy the input DataFrame (avoid modifying the original data)
        check_input=True, # whether to check the input DataFrame (validity of entries)
        engine='sklearn', # specifying the engine explicitly
        random_state=42  # ensures reproducibility
    )
    ca = ca.fit(data)  # Fit the CA model
    return ca

def plot_results(ca, data):
    # Get the coordinates
    row_coordinates = ca.row_coordinates(data)
    col_coordinates = ca.column_coordinates(data)

    # Create a plot
    plt.figure(figsize=(6, 6))
    plt.scatter(row_coordinates.iloc[:, 0], [0]*len(row_coordinates), color='blue', label='Rows (Nationality)')
    plt.scatter(col_coordinates.iloc[:, 0], [0]*len(col_coordinates), color='red', label='Columns (Handedness)')
    for i, txt in enumerate(row_coordinates.index):
        plt.annotate(txt, (row_coordinates.iloc[i, 0], 0), color='blue')
    for i, txt in enumerate(col_coordinates.index):
        plt.annotate(txt, (col_coordinates.iloc[i, 0], 0), color='red')

    plt.title('Correspondence Analysis (1D)')
    plt.xlabel('Component 1')
    plt.axhline(0, color='grey', lw=1)
    plt.legend()
    plt.grid(True)
    plt.show()

# Load and prepare data
data = load_data()

# Perform correspondence analysis
ca = perform_correspondence_analysis(data)

# Plot the results
plot_results(ca, data)
