# import streamlit as st
import requests

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st

st.title('NFT Metrics')

collections = {
    "0xbdea6285d9701c56abaa3c700403bc7cedaf8a76": "Azuki",
    "0xebfb69bb45f7db59cf30c75ee83fc9bb76c2ef49": "Bored Ape Yacht Club",
    "0x7c0af2fda1ac02840804db3c7f0f2896ec06ffd8": "Doodles",
    "0xdc5ed26e62304d5a1fcb676c7812b4cc3c1201cb": "Mutant Ape Yacht Club",
    "0xb7ab836deeda8c2ca3101baa2740e5330f0710ae": "CloneX",
    "0x938d4a74bef518505ce1542e6c88dfd476cc202e": "CryptoPunks",
    "0xde21008b47d8ede8e3cd315a3677f1c6904826a5": "Y00ts"
}

def fetchData(url):
    response = requests.get(url)
    return response.json()

data = fetchData('https://sample-62256-default-rtdb.europe-west1.firebasedatabase.app/metrics.json')

df = pd.DataFrame(data).T

# Convert the timestamp index to datetime
df.index = pd.to_datetime(df.index, unit='ms')

# Separate out the 'peg' and 'uniswap' prices into their own DataFrame
peg_uniswap_df = df[['peg', 'uniswap']]

# Drop the 'peg' and 'uniswap' columns from the original DataFrame
df.drop(['peg', 'uniswap'], axis=1, inplace=True)

# Plot the 'peg' and 'uniswap' prices
fig = go.Figure()

for column in peg_uniswap_df.columns:
    fig.add_trace(go.Scatter(x=peg_uniswap_df.index, y=peg_uniswap_df[column], mode='lines', name=column))

fig.update_layout(title='Peg and Uniswap Prices Over Time', xaxis=dict(title='Date'), yaxis=dict(title='Price'))

st.plotly_chart(fig)

# Plot the prices for each of the other addresses
for column in df.columns:
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))

    fig.update_layout(title=f'Prices Over Time for {collections[column]}', xaxis=dict(title='Date'), yaxis=dict(title='Price'))

    st.plotly_chart(fig)

# Plot all addresses together
fig = go.Figure()

for column in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=collections[column]))

fig.update_layout(title='Prices Over Time for All Addresses', xaxis=dict(title='Date'), yaxis=dict(title='Price'))
fig.update_yaxes(type="log")

st.plotly_chart(fig)
