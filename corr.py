import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# List of publicly traded Tata Group companies' ticker symbols
tata_stocks = [
    # 'TTM',  # Tata Motors
    'TCS.NS',  # Tata Consultancy Services
    'TATASTEEL.NS',  # Tata Steel
    'TATAPOWER.NS',  # Tata Power
    'TATACHEM.NS',  # Tata Chemicals
    'TATACOMM.NS',  # Tata Communications
    # 'TATACOFFEE.NS',  # Tata Coffee
    'TATACONSUM.NS',  # Tata Consumer Products
    'TATAELXSI.NS',  # Tata Elxsi
    'TATAMTRDVR.NS',  # Tata Motors DVR
    # 'TATAMTR.NS',  # Tata Motors
    'TATAPOWER.NS',  # Tata Power
    # 'TATASTEELBSL.NS',  # Tata Steel BSL
    # 'TATASTLLP.NS',  # Tata Steel Long Products
    'TITAN.NS',  # Titan Company (Tata-owned)
    'TRENT.NS',  # Trent (Tata-owned)
    'VOLTAS.NS',  # Voltas (Tata-owned)
]

# Download historical data for these stocks from Yahoo Finance
data = yf.download(tata_stocks, start='2020-01-01', end='2023-01-01')['Adj Close']

# Calculate the correlation matrix
correlation = data.corr()

# Display the correlation matrix
print("Correlation Matrix:")
print(correlation)

# Plotting the correlation matrix as a heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix of Tata Group Stocks')
plt.show()
