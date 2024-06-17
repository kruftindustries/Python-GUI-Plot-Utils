import numpy as np
from scipy.stats import norm

# Black-Scholes formula for European put
def black_scholes_eur_put(S, K, T, r, sigma):
    """
    Calculates the Black-Scholes price for a European put option.

    Parameters:
    S : float
        Current stock price
    K : float
        Strike price of the option
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying stock

    Returns:
    float
        Black-Scholes price of the put option
    """
    # Safety check to prevent log of zero
    if S == 0:
        return K * np.exp(-r * T)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    put_price = (K * np.exp(-r * T) * norm.cdf(-d2)) - (S * norm.cdf(-d1))
    return put_price

def american_put_approximation(S, K, T, r, sigma):
    """
    Approximates the price of an American put option using an adjusted Black-Scholes approach.

    Parameters:
    S : float
        Current stock price
    K : float
        Strike price of the option
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying stock

    Returns:
    float
        Approximate American put option price
    """
    adjusted_sigma = sigma * np.sqrt(2)
    adjusted_K = K * np.exp(-r * T / 2)

    put_price_european = black_scholes_put(S, adjusted_K, T, r, adjusted_sigma)
    return put_price_european
    
def black_scholes_eur_call(S, K, T, r, sigma, option_type="call"):
    """
    Calculates the Black-Scholes price for a European call or put option.

    Parameters:
    S : float
        Current stock price
    K : float
        Strike price of the option
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying stock
    option_type : str
        Type of option: "call" or "put"

    Returns:
    float
        Black-Scholes price of the option
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # "put"
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return option_price
    
def binomial_tree_american_put(S, K, T, r, sigma, N):
    """
    Prices an American call option using the binomial tree model.

    Parameters:
    S : float
        Current stock price
    K : float
        Strike price of the option
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying stock
    N : int
        Number of steps in the binomial tree

    Returns:
    float
        Price of the American call option
    """
    dt = T / N  # time step
    u = np.exp(sigma * np.sqrt(dt))  # up factor
    d = 1 / u  # down factor
    p = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability

    # Initialize asset prices at maturity
    asset_prices = np.asarray([S * u**j * d**(N - j) for j in range(N + 1)])

    # Initialize option values at maturity
    option_values = np.maximum(asset_prices - K, 0)

    # Iterate backwards through the tree
    for i in range(N - 1, -1, -1):
        option_values = (p * option_values[:-1] + (1 - p) * option_values[1:]) * np.exp(-r * dt)
        asset_prices = asset_prices[:-1] * u
        option_values = np.maximum(option_values, asset_prices - K)  # American option check

    return option_values[0]
    
def binomial_tree_american_call(S, K, T, r, sigma, N):
    """
    Prices an American put option using the binomial tree model.

    Parameters:
    S : float
        Current stock price
    K : float
        Strike price of the option
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying stock
    N : int
        Number of steps in the binomial tree

    Returns:
    float
        Price of the American put option
    """
    dt = T / N  # time step
    u = np.exp(sigma * np.sqrt(dt))  # up factor
    d = 1 / u  # down factor
    p = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability

    # Initialize asset prices at maturity
    asset_prices = np.asarray([S * u**j * d**(N - j) for j in range(N + 1)])

    # Initialize option values at maturity
    option_values = np.maximum(K - asset_prices, 0)

    # Iterate backwards through the tree
    for i in range(N - 1, -1, -1):
        option_values = (p * option_values[:-1] + (1 - p) * option_values[1:]) * np.exp(-r * dt)
        asset_prices = asset_prices[:-1] * u
        option_values = np.maximum(option_values, K - asset_prices)  # American option check

    return option_values[0]


# Example usage
current_stock_price = 90
strike_price = 100
time_to_expiration = 1  # 1 year
risk_free_rate = 0.05   # 5%
volatility = 0.2        # 20%
steps = 20            # Number of steps


eur_put_price = black_scholes_eur_put(current_stock_price, strike_price, time_to_expiration, risk_free_rate, volatility)

eur_call_price = black_scholes_eur_call(current_stock_price, strike_price, time_to_expiration, risk_free_rate, volatility, option_type="call")

tree_call = binomial_tree_american_call(current_stock_price, strike_price, time_to_expiration, risk_free_rate, volatility, steps)

tree_put = binomial_tree_american_put(current_stock_price, strike_price, time_to_expiration, risk_free_rate, volatility, steps)
print(f"The estimated Black-Scholes price for the EUR put option is: ${eur_put_price:.2f}")
print(f"The estimated Black-Scholes price for the EUR call option is: ${eur_call_price:.2f}")
print(f"The estimated adjusted binomial tree price for the put option is: ${tree_put:.2f}")
print(f"The estimated adjusted binomial tree price for the call option is: ${tree_call:.2f}")
