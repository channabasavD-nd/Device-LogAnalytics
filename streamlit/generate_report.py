import io  
import os
import zipfile
import numpy as np
import pandas as pd  
from PIL import Image
import streamlit as st  
from itertools import zip_longest
from db import get_availableDates



def get_tracebackDF(tracebacks):

    data = {
                        'Tracebacks_ndcentral': [],
                        'count_ndcentral': [],
                        'Tracebacks_inwardAnalyticsClient': [],
                        'count_inwardAnalyticsClient': [],
                        'Tracebacks_outwardAnalyticsClient': [],
                        'count_outwardAnalyticsClient': [],
                        'Tracebacks_inertialAnalyticsClient': [],
                        'count_inertialAnalyticsClient': [],
                        'Tracebacks_inferenceInertial': [],
                        'count_inferenceInertial': [],
                        'sessionID_inferenceInertial':[],
                        'Tracebacks_analyticsService': [],
                        'count_analyticsService': [],
                        'Tracebacks_inference': [],
                        'count_inference': [],
                        'sessionID_inference':[],
                        'Tracebacks_audio': [],
                        'count_audio': [],
                        'Tracebacks_health': [],
                        'count_health': [],
                        'Tracebacks_overspeedClient': [],
                        'count_overspeedClient': [],
                        'Tracebacks_reboot': [],
                        'count_reboot': [],
                        'Tracebacks_scheduler': [],
                        'count_scheduler': []
                    }
    
    for traceback in tracebacks:
        if traceback:
                services = ['ndcentral', 'inwardAnalyticsClient', 'outwardAnalyticsClient', 'inertialAnalyticsClient', 'analyticsService', 'audio', 'health', 'overspeedClient', 'reboot', 'scheduler', 'inferenceInertial', 'inference']
                for service in services:
                    for key in traceback[service]:
                        if key in data[f'Tracebacks_{service}']:
                            idx = data[f'Tracebacks_{service}'].index(key)
                            data[f'count_{service}'][idx]+=traceback[service][key]
                        else:
                            # key[:-1] in data[f'Tracebacks_{service}']
                            if service == 'health' and any('\n'.join(key.split('\n')[:-2]) in item for item in data[f'Tracebacks_{service}']):
                               
                                reccuring_traceback = ('\n'.join(key.split('\n')[:-2])) 
                                for t in data[f'Tracebacks_{service}']:
                                    if reccuring_traceback in t:
                                        idx = data[f'Tracebacks_{service}'].index(t)
                                        data[f'count_{service}'][idx]+=traceback[service][key]
                                        break
                                continue

                            data[f'Tracebacks_{service}'].append(key)
                            data[f'count_{service}'].append(traceback[service][key])
                            if service in ['inferenceInertial', 'inference']:
                                data[f'sessionID_{service}'].append(traceback[f'{service}_sessionID'][key])
                
    max_length = max(len(lst) for lst in data.values())  
        
    for key in data:  
        length_diff = max_length - len(data[key])  
        if length_diff > 0:  
            data[key] = data[key] + [np.nan] * length_diff 

    df_traceback = pd.DataFrame(data)
    df_traceback= df_traceback.dropna(axis=1, how='all')
    df_traceback = df_traceback.dropna(how='all')
    column_counts = df_traceback.count(axis=0)
    sorted_columns = column_counts.sort_values(ascending=False)
    df_traceback = df_traceback[sorted_columns.index]

    return df_traceback
    
def To_DF(report, tracebacks):
    df = pd.DataFrame.from_dict(report, orient='index').T
    df_traceback = get_tracebackDF(tracebacks)
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


def generate_HTML(df, pieData, total_documents):

    with open(f"{st.session_state['report_folder']}/dashboard.html", "w") as f:  
        
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
                img = Image.open(f"{st.session_state['report_folder']}/images/{chart_name}.png")
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
            f.write(f"<h3>{section_title}:</h3>")
            f.write("<div class='container'>")
            for chart_name in charts:
                if section_title == 'Inference':
                    service = "Inward" if "inward" in chart_name else "Outward"
                    sum_count = 0
                    if 'count_inference' in df.columns:
                        sum_count = df['count_inference'].sum()
                    f.write(f"<div class='chart'>")
                    f.write(f"<p style='text-align: center;'>{service}</p><img src='images/{chart_name}.png' alt='{chart_name}'>")
                    f.write(f"<p style='text-align: left;'>Average processing time: {pieData[f'{service.lower()}NRT']['processing_time']/total_documents}</p>")
                    f.write(f"<p style='text-align: left;'>Missing summary files: {total_documents-pieData[f'{service.lower()}NRT']['summaryFile_status']}</p>")
                    if chart_name == 'inwardNRT_chart':
                        f.write(f"<p style='text-align: left;'>traceback count: {int(sum_count)}</p>")
                    f.write("</div>")
                    continue
                service = "Inward" if "inward" in chart_name else "Outward"
                sum_count = 0
                if 'Client' in section_title and f'count_{service.lower()}AnalyticsClient' in df.columns:
                    sum_count = df[f'count_{service.lower()}AnalyticsClient'].sum()
                if 'Service' in section_title and 'count_analyticsService' in df.columns:
                    sum_count = df['count_analyticsService'].sum()
                f.write(f"<div class='chart'>")
                f.write(f"<p style='text-align: center;'>{service}</p><img src='images/{chart_name}.png' alt='{chart_name}'>")
                if chart_name != 'outwardAnalytics_chart':
                    f.write(f"<p style='text-align: left;'>traceback count: {int(sum_count)}</p>")
                f.write("</div>")
            # df.loc[df['alphabet'] == 'A', 'values'].sum()

            f.write("</div>")
        f.write("</body></html>")
            # f.write(f"<h5 style='text-align: left;'>Total tracebacks : 10|Events detected : 202</h5>")
        # st.success("HTML File successfully generated")

def zip_folder(folder_path, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

def process_df(df):
    traceback_df =  pd.DataFrame(columns=['Tracebacks', 'Count', 'Service', 'SessionID'])
    obs_df = pd.DataFrame(columns=['Missing_obsData', 'Service'])
    sessionDrop_df = pd.DataFrame(columns=['Session_Drop', 'service', 'reason'])
    summaryFile_df = pd.DataFrame(columns=['Missing_summaryFiles', 'Service'])
    NRT_df = pd.DataFrame(columns=['NRT_failure', 'service'])

    for column in df.columns:
        if 'Tracebacks' in column:
            for i in range(len(df[column])):
                traceback = df[column][i]
                Service = column.split('_')[-1]
                Count = df[('count_'+ Service)][i]
                sessioID = None
                # st.write(traceback)
                if 'inference' in column:
                    sessioID = df[('sessionID_'+ Service)][i]
                if traceback and not pd.isna(traceback):
                    traceback_df = traceback_df._append({'Tracebacks':traceback, 'Count':Count, 'Service':Service, 'SessionID':sessioID}, ignore_index=True)
    traceback_df = traceback_df.dropna(axis=1, how='all')
    traceback_df = traceback_df.dropna(how='all')
    traceback_df = traceback_df.sort_values(by='Count', ascending=False).reset_index(drop=True)
    # st.write(traceback_df)
    return traceback_df

    
def gen_report(report, tracebacks, PieData, total_documents):
    df, df_traceback = To_DF(report, tracebacks)
    st.write("Summary Report")
    st.write(df)
    # inference_tracebacks = get_inference_tracebacks()
    # if not inference_tracebacks.empty:
    #     df_traceback = pd.concat([df_traceback, inference_tracebacks], axis=1)
    #     df_traceback = df_traceback.dropna(axis=1, how='all')
    #     df_traceback = df_traceback.dropna(how='all')
    generate_HTML(df_traceback, PieData, total_documents)
    df_traceback = process_df(df_traceback)
    if not df_traceback.empty:
        st.write("Traceback Report")
        st.write(df_traceback)
        empty_df = pd.DataFrame(index=df_traceback.index, columns=['',''])
        df =  pd.concat([df_traceback, empty_df, df], axis=1)
        # df = df.dropna(axis=1, how='all')
        # df = df.dropna(how='all')
    else:
        st.info('No tracebacks found in logs')

   
    xlsx = convert_df(df)
    file_name = os.path.join(st.session_state['report_folder'], f"report-{st.session_state['deviceID']}-{st.session_state['ota_version']}.xlsx")
    # with open(file_name, "wb") as f:
    #     f.write(xlsx)
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Iterate over each column
        for col_idx, col in enumerate(df.columns, start=1):
            # Get the maximum length of values in the column
            if col not in  ['Count','', 'Tracebacks'] :
                max_length = max(df[col].astype(str).str.len().max(), len(col))

            # Set the column width to the maximum length plus some padding
                worksheet.column_dimensions[worksheet.cell(row=1, column=col_idx).column_letter].width = max_length + 2

        # Save the Excel file
        writer._save()

    zip_filename = st.session_state['report_folder']
    zip_folder(zip_filename, f"{zip_filename}.zip")

    # st.download_button( 
    #     label="Download report",  
    #     data=xlsx,  
    #     file_name=f"report-{st.session_state['deviceID']}-{st.session_state['ota_version']}({st.session_state['date']}).xlsx",  
    #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  
    # )  
    with open(f"{zip_filename}.zip", "rb") as f:
        st.download_button(label="Download Report", data=f, file_name=f"{zip_filename}.zip", mime="application/zip")


   

