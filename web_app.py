import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import sys
import openpyxl
import sl_helper as sl_help
sys.path.append("/Users/cr591/OneDrive - University of Exeter/Desktop/diametrics/diametrics")
import metrics as cgm
# To set up a streamlit environment with SimPy available:
# conda create -n streamlit python=3.8
# conda activate streamlit
# conda install matplotlib numpy pandas
# pip install simpy streamlit

# Add a title
st.title('Diametrics')
st.write("This is a freely available tool to calculate the metrics of diabetes control using the Python package"
         " Diametrics. Please ensure that your files are ")
# Upload csv
files = st.file_uploader('Upload Excel or CSV files', accept_multiple_files=True)

# Determine time interval
interval = st.radio("Time interval between readings",
                 ('5 mins', '15 mins', 'Calculate automatically'))
st.write('Select the time interval between readings. If it\'s a Dexcom or Medtronic then it will be 5 mins, Libre is'
         '15 mins')
if interval == '5 mins':
    time_int = 5
elif interval == '15 mins':
    time_int = 15
else:
    time_int = None # calculate time interval

# Determine how to crunch multiple files
multiple_files = st.radio("Name of ID column if present...",
                 ('Use filename as ID', 'Calculate separately'))
st.write('If use filename as ID is selected, the name of the file will be used as ID and the results will be output as'
         'one table with the filename as reference')
if multiple_files == 'Use filename as ID':
    as_id = True
else:
    as_id = False

id_colname = None

# Determine how to crunch multiple files
breakdown_by_day = st.radio("Breakdown by day...",
                 ('Yes', 'No'))
st.write('Select yes if you want a day-by-day breakdown with all the metrics calculated for each day')
if breakdown_by_day == 'Yes':
    by_day = True
else:
    by_day = False


def process_file(files):
    results_frame = pd.DataFrame()
    for file in files:
        print('########## FILE #######')
        print(file)
        # Load file
        try:
            df = pd.read_excel(file)
        except Exception: # sort this out
            print('not excel')
            try:
                df = pd.read_csv(file, names=[i for i in range(30)])
            except Exception:
                st.write('File in wrong format, must be Excel or CSV')
        df.replace({'High': 22.2, 'Low': 2.2, 'HI':22.2, 'LO':2.2, 'hi':22.2, 'lo':2.2}, inplace=True)
        # Preprocess
        df_preprocessed = sl_help.preprocess_data(df, id_colname)
        # If there's no ID column, use filename as ID
        if id_colname is None:
            df_preprocessed['ID'] = file.name.rsplit('.', 1)[0]
        # Calculate metrics
        df_preprocessed.glc = pd.to_numeric(df_preprocessed.glc)
        results = cgm.all_metrics(df_preprocessed, 'time', 'glc', 'ID', time_int)
        #st.write(results)
        results_frame = results_frame.append(results)
    #results_frame = pd.DataFrame(results_list)
    results_frame.reset_index(drop=True, inplace=True)
    st.write(results_frame)


'''# Process file
def process_file(file):
    print('####### FILE #########')
    print(file)
    try:
        df = pd.read_excel(file)
    except Exception:
        print('here!')
        df = pd.read_csv(file)
    results = cgm.all_metrics(df, 'time', 'glc', 'ID', time_int)
    st.write(results)
'''


if st.button('Process files'):
    process_file(files)

# Run app from terminal with `streamlit run basic_examples.py"


# Show a matplotlib chart based on user input
power = st.slider('Power', min_value=0, max_value=5, value=2)


def draw_chart():
    # Calculate results
    x = np.arange(0, 10.1, 0.1)
    y = x ** power

    # Draw MatPltLib chart
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.plot(x, y, label=power)
    ax.set_xlim(0, 10)
    ax.set_ylim(0)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend(title='Power')

    # Render chart with streamlit
    st.pyplot(fig)


if st.button('Draw chart'):
    draw_chart()

# Produce a map from random Lat Long
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

