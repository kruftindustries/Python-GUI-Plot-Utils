import numpy as np

def monte_carlo_simulation(initial_investment, years, trials, min_return, max_return):
    """
    Simulate the future value of an investment given a range of possible annual returns.
    
    Parameters:
        initial_investment (float): The amount of money initially invested.
        years (int): The number of years to run the simulation.
        trials (int): The number of simulation trials to run.
        min_return (float): The minimum annual return rate (as a percentage).
        max_return (float): The maximum annual return rate (as a percentage).
        
    Returns:
        float: The average estimated future value of the investment after the specified number of years.
    """
    # Store all ending values from each simulation
    end_values = []

    for _ in range(trials):
        # Start with the initial investment
        future_value = initial_investment
        
        # Simulate each year
        for _ in range(years):
            # Random annual return for this year, converted from percentage to decimal
            annual_return = np.random.uniform(min_return, max_return) / 100
            # Update the investment value
            future_value *= (1 + annual_return)
        
        # Append the value at the end of the period to the list
        end_values.append(future_value)
    
    # Calculate the average of all simulated future values
    average_future_value = np.mean(end_values)
    return average_future_value

# Example usage
initial_investment = 10000  # $10,000 initial investment
years = 10                  # Over 10 years
trials = 1000               # 1000 simulation trials
min_return = -10            # Minimum return of -10%
max_return = 20             # Maximum return of 20%

average_future_value = monte_carlo_simulation(initial_investment, years, trials, min_return, max_return)
print(f"Average Estimated Future Value: ${average_future_value:.2f}")
