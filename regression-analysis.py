#python -m pip install -U scikit-learn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Create or load data
data = {
    'X': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'Y': [1.5, 3.5, 4.1, 5.9, 7.2, 8.5, 10.4, 12.3, 13.7]
}
df = pd.DataFrame(data)

# Prepare data
X = df[['X']]  # Features (independent variables)
Y = df['Y']    # Target (dependent variable)

# Splitting the data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

# Create a linear regression model
model = LinearRegression()

# Train the model
model.fit(X_train, Y_train)

# Predict using the model
Y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(Y_test, Y_pred)
r2 = r2_score(Y_test, Y_pred)

print("Mean Squared Error:", mse)
print("R2 Score:", r2)

# Plotting the results
plt.scatter(X, Y, color='blue')  # Actual points
plt.plot(X, model.predict(X), color='red')  # Regression line
plt.title('Linear Regression')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()
