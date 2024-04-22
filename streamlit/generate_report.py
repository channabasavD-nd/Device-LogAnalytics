import io  
import numpy as np
import pandas as pd  
from PIL import Image
import streamlit as st  
from itertools import zip_longest
from db import get_availableDates

  
def To_DF(report, traebacks):
    df = pd.DataFrame.from_dict(report, orient='index').T
    df_traceback = pd.DataFrame()
    for traceback in traebacks:
        if traceback:
        # data = {'Tracebacks_ndcentral': list(traebacks['ndcentral'].keys()),'count':list(traebacks['ndcentral'].values()), 'Tracebacks_inwardAnalyticsClient':list(traebacks['inwardAnalyticsClient'].keys()), 'count':list(traebacks['inwardAnalyticsClient'].values()), 'Tracebacks_outwardAnalyticsClient':list(traebacks['outwardAnalyticsClient'].keys()), 'count':list(traebacks['outwardAnalyticsClient'].values()), 'Tracebacks_inertialAnalyticsClient':list(traebacks['inertialAnalyticsClient'].keys()) ,'count':list(traebacks['inertialAnalyticsClient'].values()), 'Tracebacks_inferenceInertial':list(traebacks['inferenceInertial'].keys()) ,'count':list(traebacks['inferenceInertial'].values()), 'Tracebacks_analyticsService':list(traebacks['analyticsService'].keys()) ,'count':list(traebacks['analyticsService'].values())}
            inferenceInertial_sessionIDs = []
            inference_sessionIDs = []
            if traceback['inferenceInertial_sessionID']:
                for key in traceback['inferenceInertial'].keys():
                    inferenceInertial_sessionIDs.append(traceback['inferenceInertial_sessionID'][key])
            if traceback['inference_sessionID']:
                for key in traceback['inference'].keys():
                    inference_sessionIDs.append(traceback['inference_sessionID'][key])

            data = {
                        'Tracebacks_ndcentral': list(traceback['ndcentral'].keys()),
                        'count_ndcentral': list(traceback['ndcentral'].values()),
                        'Tracebacks_inwardAnalyticsClient': list(traceback['inwardAnalyticsClient'].keys()),
                        'count_inwardAnalyticsClient': list(traceback['inwardAnalyticsClient'].values()),
                        'Tracebacks_outwardAnalyticsClient': list(traceback['outwardAnalyticsClient'].keys()),
                        'count_outwardAnalyticsClient': list(traceback['outwardAnalyticsClient'].values()),
                        'Tracebacks_inertialAnalyticsClient': list(traceback['inertialAnalyticsClient'].keys()),
                        'count_inertialAnalyticsClient': list(traceback['inertialAnalyticsClient'].values()),
                        'Tracebacks_inferenceInertial': list(traceback['inferenceInertial'].keys()),
                        'count_inferenceInertial': list(traceback['inferenceInertial'].values()),
                        'sessionID_inferenceInertial':inferenceInertial_sessionIDs,
                        'Tracebacks_analyticsService': list(traceback['analyticsService'].keys()),
                        'count_analyticsService': list(traceback['analyticsService'].values()),
                        'Tracebacks_inference': list(traceback['inference'].keys()),
                        'count_inference': list(traceback['inference'].values()),
                        'sessionID_inference':inference_sessionIDs,
                        'Tracebacks_audio': list(traceback['audio'].keys()),
                        'count_audio': list(traceback['audio'].values()),
                        'Tracebacks_health': list(traceback['health'].keys()),
                        'count_health': list(traceback['health'].values()),
                        'Tracebacks_overspeedClient': list(traceback['overspeedClient'].keys()),
                        'count_overspeedClient': list(traceback['overspeedClient'].values()),
                        'Tracebacks_reboot': list(traceback['reboot'].keys()),
                        'count_reboot': list(traceback['reboot'].values()),
                        'Tracebacks_scheduler': list(traceback['scheduler'].keys()),
                        'count_scheduler': list(traceback['scheduler'].values())
                    }

            max_length = max(len(lst) for lst in data.values())  
        
            for key in data:  
                length_diff = max_length - len(data[key])  
                if length_diff > 0:  
                    data[key] = data[key] + [np.nan] * length_diff 

            df_traceback_temp = pd.DataFrame(data)
            df_traceback = pd.concat([df_traceback, df_traceback_temp], ignore_index=True)
        # df =  pd.concat([df_report, df_traceback], axis=1)
    df_traceback= df_traceback.dropna(axis=1, how='all')
    df_traceback = df_traceback.dropna(how='all')
    column_counts = df_traceback.count(axis=0)
    sorted_columns = column_counts.sort_values(ascending=False)
    df_traceback = df_traceback[sorted_columns.index]  

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
    column_counts = df.count(axis=0)
    sorted_columns = column_counts.sort_values(ascending=False)
    df = df[sorted_columns.index]

    return df, df_traceback

@st.cache_data 
def convert_df(df):   

    stream = io.BytesIO()  
    df.to_excel(stream, index=False)  
    return stream.getvalue() 


def generate_HTML():

    with open("dashboard.html", "w") as f:  
        
        f.write("<html><head><title>Log Analytics Report</title>")
        f.write("<style>")
        f.write("body { font-family: Arial, sans-serif; background-color: #dcd2d2; padding: 20px; }")
        f.write("h1 { color: #333; text-align: center; }")
        f.write(".container { display: flex; flex-wrap: wrap; justify-content: center; }")
        f.write(".chart { margin: 20px; }")
        f.write("</style>")
        f.write("</head><body>")
        
        f.write("<h1>Log Analytics Report</h1>")
        f.write(f"<h3>Device_ID : {st.session_state['deviceID']}</h3>")
        f.write(f"<h3>OTA_version : {st.session_state['ota_version']}</h3>")
        if st.session_state['date'] :
            f.write(f"<h3>Date : {st.session_state['date']}</h3>")
        else:
            dates = get_availableDates()
            dates = sorted(dates)
            f.write(f"<h3>Date : From {dates[0]} to {dates[-1]}</h3>")

        max_width = 0
        max_height = 0
        sections = {
            "Analytics Service": ["inwardAnalytics_chart", "outwardAnalytics_chart"],
            "Analytics Client": ["inwardClient_chart", "outwardClient_chart"],
            "Inference": ["inwardNRT_chart", "outwardNRT_chart"]
        }
        
        for section_title, charts in sections.items():
            f.write("<div class='container'>")
            for chart_name in charts:
                # Get dimensions of current image
                img = Image.open(f"{chart_name}.png")
                width, height = img.size
                if width > max_width:
                    max_width = width
                if height > max_height:
                    max_height = height
                img.close()
            f.write("</div>")

        f.write("<style>")
        f.write(f".chart img {{ width: {max_width}px; height: {max_height}px; }}")
        f.write("</style>")

        for section_title, charts in sections.items():
            f.write(f"<h3>{section_title}</h3>")
            f.write("<div class='container'>")
            for chart_name in charts:
                service = "Inward" if "inward" in chart_name else "Outward"
                f.write(f"<div class='chart'><p style='text-align: center;'>{service}</p><img src='{chart_name}.png' alt='{chart_name}'></div>")
            f.write("</div>")
        
        f.write("</body></html>")
        st.success("HTML File successfully generated")
     
   
def gen_report(report, tracebacks):
    df, df_traceback = To_DF(report, tracebacks)
    st.write("Summary Report")
    st.write(df)
    # inference_tracebacks = get_inference_tracebacks()
    # if not inference_tracebacks.empty:
    #     df_traceback = pd.concat([df_traceback, inference_tracebacks], axis=1)
    #     df_traceback = df_traceback.dropna(axis=1, how='all')
    #     df_traceback = df_traceback.dropna(how='all')

    if not df_traceback.empty:
        st.write("Traceback Report")
        st.write(df_traceback)
        df =  pd.concat([df, df_traceback], axis=1)
        df = df.dropna(axis=1, how='all')
        df = df.dropna(how='all')
    else:
        st.info('No tracebacks found in logs')

    xlsx = convert_df(df)  
    st.download_button( 
        label="Download report",  
        data=xlsx,  
        file_name=f"report-{st.session_state['deviceID']}-{st.session_state['ota_version']}({st.session_state['date']}).xlsx",  
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  
    )  
   

