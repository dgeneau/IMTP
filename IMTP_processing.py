import pandas as pd
import numpy as np 
from nptdms import TdmsFile
import plotly.graph_objs as go

import streamlit as st
from datetime import datetime


def group_data(array, threshold):
    groups = []
    current_group = [array[0]]

    for i in range(1, len(array)):
        diff = array[i] - array[i - 1]
        if diff > threshold:
            groups.append(current_group)
            current_group = [array[i]]
        else:
            current_group.append(array[i])
    if len(current_group) >= 2000:  # Append the last group if it has at least 3 items
        
        groups.append(current_group)
    else: 
        pass

    return groups


st.set_page_config(layout='wide')
st.title('IMTP Post Processing')



# Path to your TDMS file
tdms_file_path_L = st.file_uploader('Upload TDMS file')

if tdms_file_path_L  is None: 
    st.header('Select File to Analyze')
    st.stop()

tdms_file = TdmsFile.read(tdms_file_path_L)

file_name = tdms_file_path_L.name.split('.')[0]
date = file_name.split('_')[0]
date_object = datetime.strptime(date, "%d%m%Y")

# Format the datetime object into the desired output string
formatted_date = date_object.strftime("%d %B %Y")


name_full = file_name.split('_')[1]
st.subheader(name_full)
st.write(formatted_date)


# Load the TDMS file
#tdms_file = TdmsFile.read(tdms_file_path)

group_names = ['Left', 'Right']

# List to store individual group DataFrames
df_list = []

for group_name in group_names:
    group = tdms_file[group_name]

    # Build a dictionary of channel data
    data = {f"{group_name}_{channel.name}": channel[:] for channel in group.channels()}

    # Create the DataFrame
    df = pd.DataFrame(data)

    df_list.append(df)

# Concatenate all DataFrames side-by-side
combined_df = pd.concat(df_list, axis=1)

combined_df['Total_Fx'] = combined_df['Left_Fx'] + combined_df['Right_Fx']
combined_df['Total_Fy'] = combined_df['Left_Fy'] + combined_df['Right_Fy']
combined_df['Total_Fz'] = combined_df['Left_Fz'] + combined_df['Right_Fz']

start_col, BW_col = st.columns(2)
with start_col:
    start = st.number_input('Crop Onset to Body Weight Quiet Standing', 0)

combined_df = combined_df.iloc[start:]

with BW_col:
    #Selecting Body weight based on average quiet standing. Can overide with input
    BW_N = st.number_input('Quiet Standing (N)', value = np.mean(combined_df['Total_Fz'].iloc[0:1000]))


cropping_df = np.where(combined_df['Total_Fz'] >= BW_N+150)[0]
section_indexes = group_data(np.array(cropping_df), 150)


fig = go.Figure()
for section in section_indexes:
    if len(section)>2000:
        fig.add_shape(
            type="rect",
            x0=section[0],
            x1=section[-1]+1,
            y0=0,
            y1 = round(np.max(combined_df['Total_Fz']))+200, 
            fillcolor="grey",
            opacity=0.2)
    else: 
        pass


fig.add_trace(go.Scattergl(
    y = combined_df['Total_Fz'], 
    name = 'Total Vertical Force', 
    mode = 'markers+lines',
    line = dict(color = 'black', width = 2), 
    marker = dict(color = 'black', size = 2)
))
fig.add_trace(go.Scattergl(
    y = combined_df['Left_Fz'], 
    name = 'Left', 
    mode = 'lines',
    line = dict(color = 'green')
))
fig.add_trace(go.Scattergl(
    y = combined_df['Right_Fz'], 
    name = 'Right',  
    mode = 'lines',
    line = dict(color = 'red')
))

fig.add_hline(y=BW_N, line_dash="dot", line_color="red")
fig.update_layout(title = '<b>Force Time Trace</b>')
st.plotly_chart(fig)


combined_df['Time'] = np.array(range(0,len(combined_df+1)))/1000


col1, col2, col3, col4 = st.columns(4)

pull_list = []
total_avg = []
left_avg = []
right_avg = []
total_peak = []
left_peak = []
right_peak = []

count = 0
for section in section_indexes: 
    if len(section) >2000:
        count += 1
        pull_list.append(count)
        with col1:
            st.header(f'Pull {count}:')
            st.header(f'')
            st.header(f'')
        with col2: 
            total_avg.append(round(np.mean(combined_df['Total_Fz'].iloc[section]), 1))
            total_peak.append(round(np.max(combined_df['Total_Fz'].iloc[section]), 1))
            st.metric('Average Force (N), (N/Kg)', f'{round(np.mean(combined_df['Total_Fz'].iloc[section]), 1)}, {round(np.mean(combined_df['Total_Fz'].iloc[section])/(BW_N/9.81), 2)}' )
            st.metric('Peak Force (N), (N/Kg)', f'{round(np.max(combined_df['Total_Fz'].iloc[section]), 1)}, {round(np.max(combined_df['Total_Fz'].iloc[section])/(BW_N/9.81), 2)}')
            st.header(f'')
        with col3: 
            left_avg.append(round(np.mean(combined_df['Left_Fz'].iloc[section]), 1))
            left_peak.append(round(np.max(combined_df['Left_Fz'].iloc[section]), 1))
            st.metric('Average Left (N), (N/Kg)', f'{round(np.mean(combined_df['Left_Fz'].iloc[section]), 1)}, {round(np.mean(combined_df['Left_Fz'].iloc[section])/(BW_N/9.81), 2)}')
            st.metric('Peak Left (N), (N/Kg)', f'{round(np.max(combined_df['Left_Fz'].iloc[section]), 1)}, {round(np.max(combined_df['Left_Fz'].iloc[section])/ (BW_N/9.81), 2)}')
            st.header(f'')
        with col4: 
            right_avg.append(round(np.mean(combined_df['Right_Fz'].iloc[section]), 1))
            right_peak.append(round(np.mean(combined_df['Right_Fz'].iloc[section]), 1))
            st.metric('Average Right (N), (N/Kg)', f'{round(np.mean(combined_df['Right_Fz'].iloc[section]), 1)}, {round(np.mean(combined_df['Right_Fz'].iloc[section])/(BW_N/9.81), 2)}')
            st.metric('Peak Right (N), (N/Kg)', f'{round(np.max(combined_df['Right_Fz'].iloc[section]), 1)}, {round(np.max(combined_df['Right_Fz'].iloc[section])/(BW_N/9.81), 2)}')
            st.header(f'')

    else: 
        pass


summary_data  = pd.DataFrame()
summary_data['Pull Number'] = pull_list
summary_data['Name'] = name_full
summary_data['BW (Kg)'] = BW_N/9.81
summary_data['Left Average Force (N)'] = left_avg
summary_data['Right Average Force (N)'] = right_avg
summary_data['Left Average Force (N/Kg)'] = np.array(left_avg)/(BW_N/9.81)
summary_data['Right Average Force (N/Kg)'] = np.array(right_avg)/(BW_N/9.81)
summary_data['Asymmetry Average %'] =  (np.array(right_avg)-np.array(left_avg))/(np.array(right_avg)+np.array(left_avg))*100
summary_data['Left Peak Force (N)'] = left_peak
summary_data['Right Peak Force (N)'] = right_peak
summary_data['Left Peak Force (N/Kg)'] = np.array(left_peak)/(BW_N/9.81)
summary_data['Right Peak Force (N/Kg)'] = np.array(right_peak)/(BW_N/9.81)
summary_data['Asymmetry Peak %'] =  (np.array(right_peak)-np.array(left_peak))/(np.array(right_peak)+np.array(left_peak))*100

st.write(summary_data)

st.download_button(
    label="Download CSV",
    data=summary_data.to_csv().encode("utf-8"),
    file_name=f"IMTP_data_{name_full}.csv",
    icon=":material/download:",
)

#st.write(stream_start, stream_end)
#st.write(combined_df)
