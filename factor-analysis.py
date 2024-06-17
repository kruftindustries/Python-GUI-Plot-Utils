#python -m pip install factor_analyzer
import pandas as pd
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo

# Sample data loading. Replace this with your dataset
def load_data():
    # Creating a simple dataset
    data = {
        'Variable1': [4.2, 5.1, 5.0, 3.9, 4.5],
        'Variable2': [3.9, 4.8, 4.9, 3.6, 4.2],
        'Variable3': [2.1, 2.4, 2.3, 2.1, 2.3],
        'Variable4': [3.5, 4.0, 3.8, 3.2, 3.7]
    }
    df = pd.DataFrame(data)
    return df

# Load dataset
df = load_data()

# Check the suitability of data for factor analysis
chi_square_value, p_value = calculate_bartlett_sphericity(df)
kmo_all, kmo_model = calculate_kmo(df)
print(f"Bartlett's test chi-squared value: {chi_square_value}, p-value: {p_value}")
print(f"KMO test value: {kmo_model}")

# Create factor analysis object and perform factor analysis
fa = FactorAnalyzer(n_factors=2, rotation='varimax')
fa.fit(df)

# Check Eigenvalues
ev, v = fa.get_eigenvalues()
print(f"Eigenvalues: {ev}")

# Get loadings
loadings = fa.loadings_
print("Factor Loadings:")
print(loadings)

# Get variance of each factors
variance, proportional_var, cumulative_var = fa.get_factor_variance()
print("Variance explained by each factor:")
print(proportional_var)
print("Cumulative Variance explained by all factors:")
print(cumulative_var)

# Interpretation can be added based on the loadings and variance explained
