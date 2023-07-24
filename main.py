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

def flip_json(json_obj):
    flipped_json = {v: k for k, v in json_obj.items()}
    return flipped_json

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

# Get leaderboard data

userAddresses = fetchData('https://sample-62256-default-rtdb.europe-west1.firebasedatabase.app/substrate.json')

userAddresses = flip_json(userAddresses)

data = fetchData('https://sample-62256-default-rtdb.europe-west1.firebasedatabase.app/leaderboardTimestamp.json')

print(data)

# Preprocess the data
data_frames = {datetime.fromtimestamp(int(ts)/1000): pd.DataFrame(values, columns=['Address', 'Value']) for ts, values in data.items()}

# Convert the datetime objects to a list of strings for use with the selectbox
dates = list(map(lambda dt: dt.strftime('%Y-%m-%d'), data_frames.keys()))

# Get the unique dates
unique_dates = list(set(dates))

# Use the selectbox widget to let the user select a date
selected_date_str = st.selectbox('Select a date', unique_dates)

# Convert the selected date string back to a datetime object
selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')

for dt, df in data_frames.items():
    df['Address'] = df['Address'].map(userAddresses)

st.write("Leaderboard for", selected_date_str)

# Iterate over the data_frames to find and display tables for the selected date
for dt, df in data_frames.items():
    if dt.date() == selected_date.date():
        # Print the timestamp as the title of the table
        st.subheader(dt.strftime('%H:%M:%S') + ' UTC')
        st.write(df)
