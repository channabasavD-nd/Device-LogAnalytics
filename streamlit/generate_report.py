import io  
import numpy as np
import pandas as pd  
import streamlit as st  
from itertools import zip_longest
  
def To_DF(report, traebacks):
    df_report = pd.DataFrame.from_dict(report, orient='index').T
    if traebacks :
        data = {'Traacebacks_ndcentral': traebacks['ndcentral'].keys(), 'Traacebacks_inwardAnalyticsClient':traebacks['inwardAnalyticsClient'].keys(), 'Traacebacks_outwardAnalyticsClient':traebacks['outwardAnalyticsClient'].keys(), 'Traacebacks_inertialAnalyticsClient':traebacks['inertialAnalyticsClient'].keys(), 'Traacebacks_inferenceInertial':traebacks['inferenceInertial'].keys(), 'Traacebacks_analyticsService':traebacks['analyticsService'].keys()}
        max_length = max(len(lst) for lst in data.values())  
    
        for key in data:  
            length_diff = max_length - len(data[key])  
            if length_diff > 0:  
                data[key] = data[key] + [np.nan] * length_diff 

        df_traceback = pd.DataFrame(data)
        df =  pd.concat([df_report, df_traceback], ignore_index=True)
    else:
        st.warning('Traceback stats missing')
        df = df_report

    inward_subDF = pd.DataFrame.from_dict(report["inward_sessionDrop"], orient='index')
    outward_subDF = pd.DataFrame.from_dict(report["outward_sessionDrop"], orient='index')
    for label, row in inward_subDF.iterrows():
        df[('inward_sessionDrop', label)] = row
    for label, row in outward_subDF.iterrows():
        df[('outward_sessionDrop', label)] = row

    df = df.drop(columns=['inward_sessionDrop', 'outward_sessionDrop'])  
    df = df.drop('unprocessed_events_outwardClient' , axis=1)
    df = df.drop('unprocessed_events_inwardClient' , axis=1)
    df = df.dropna(axis=1, how='all')
    df = df.dropna(how='all')

    return df

@st.cache_data 
def convert_df(df):   

    stream = io.BytesIO()  
    df.to_excel(stream, index=False)  
    return stream.getvalue()  
   
def gen_report(report, tracebacks):
    df = To_DF(report, tracebacks)
    st.write(df)
    xlsx = convert_df(df)  
    st.download_button(  
        label="Download report",  
        data=xlsx,  
        file_name=f"report-{st.session_state['deviceID']}-{st.session_state['ota_version']}({st.session_state['date']}).xlsx",  
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  
    )  


