import io  
import numpy as np
import pandas as pd  
import streamlit as st  
from itertools import zip_longest

  
def To_DF(report, traebacks):
    df = pd.DataFrame.from_dict(report, orient='index').T
    if traebacks :
        # data = {'Tracebacks_ndcentral': list(traebacks['ndcentral'].keys()),'count':list(traebacks['ndcentral'].values()), 'Tracebacks_inwardAnalyticsClient':list(traebacks['inwardAnalyticsClient'].keys()), 'count':list(traebacks['inwardAnalyticsClient'].values()), 'Tracebacks_outwardAnalyticsClient':list(traebacks['outwardAnalyticsClient'].keys()), 'count':list(traebacks['outwardAnalyticsClient'].values()), 'Tracebacks_inertialAnalyticsClient':list(traebacks['inertialAnalyticsClient'].keys()) ,'count':list(traebacks['inertialAnalyticsClient'].values()), 'Tracebacks_inferenceInertial':list(traebacks['inferenceInertial'].keys()) ,'count':list(traebacks['inferenceInertial'].values()), 'Tracebacks_analyticsService':list(traebacks['analyticsService'].keys()) ,'count':list(traebacks['analyticsService'].values())}
        inferenceInertial_sessionIDs = []
        inference_sessionIDs = []
        if traebacks['inferenceInertial_sessionID']:
            for key in traebacks['inferenceInertial'].keys():
                inferenceInertial_sessionIDs.append(traebacks['inferenceInertial_sessionID'][key])
        if traebacks['inference_sessionID']:
            for key in traebacks['inference'].keys():
                inference_sessionIDs.append(traebacks['inference_sessionID'][key])

        data = {
                    'Tracebacks_ndcentral': list(traebacks['ndcentral'].keys()),
                    'count_ndcentral': list(traebacks['ndcentral'].values()),
                    'Tracebacks_inwardAnalyticsClient': list(traebacks['inwardAnalyticsClient'].keys()),
                    'count_inwardAnalyticsClient': list(traebacks['inwardAnalyticsClient'].values()),
                    'Tracebacks_outwardAnalyticsClient': list(traebacks['outwardAnalyticsClient'].keys()),
                    'count_outwardAnalyticsClient': list(traebacks['outwardAnalyticsClient'].values()),
                    'Tracebacks_inertialAnalyticsClient': list(traebacks['inertialAnalyticsClient'].keys()),
                    'count_inertialAnalyticsClient': list(traebacks['inertialAnalyticsClient'].values()),
                    'Tracebacks_inferenceInertial': list(traebacks['inferenceInertial'].keys()),
                    'count_inferenceInertial': list(traebacks['inferenceInertial'].values()),
                    'sessionID_inferenceInertial':inferenceInertial_sessionIDs,
                    'Tracebacks_analyticsService': list(traebacks['analyticsService'].keys()),
                    'count_analyticsService': list(traebacks['analyticsService'].values()),
                    'Tracebacks_inference': list(traebacks['inference'].keys()),
                    'count_inference': list(traebacks['inference'].values()),
                    'sessionID_inference':inference_sessionIDs,
                    'Tracebacks_audio': list(traebacks['audio'].keys()),
                    'count_audio': list(traebacks['audio'].values()),
                    'Tracebacks_health': list(traebacks['health'].keys()),
                    'count_health': list(traebacks['health'].values()),
                    'Tracebacks_overspeedClient': list(traebacks['overspeedClient'].keys()),
                    'count_overspeedClient': list(traebacks['overspeedClient'].values()),
                    'Tracebacks_reboot': list(traebacks['reboot'].keys()),
                    'count_reboot': list(traebacks['reboot'].values()),
                    'Tracebacks_scheduler': list(traebacks['scheduler'].keys()),
                    'count_scheduler': list(traebacks['scheduler'].values())
                }

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
        # df =  pd.concat([df_report, df_traceback], axis=1)
    else:
        df_traceback = pd.DataFrame()

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

# def get_inference_tracebacks():
#     documents = get_tracebacks_DB()
#     tracebacks_inference= []
#     session_ids_inference = []
#     service_inference = []
#     # st.write(documents)
#     for document in documents:
#         if document['inference']['outward_NRT']['traceback'] != 'NA':
#             tracebacks_inference.append(document['inference']['outward_NRT']['traceback'])
#             session_ids_inference.append(document['session_ID'])
#             service_inference.append('outward_NRT')
#         if document['inference']['inward_NRT']['traceback'] != 'NA':
#             tracebacks_inference.append(document['inference']['inward_NRT']['traceback'])
#             session_ids_inference.append(document['session_ID'])
#             service_inference.append('inward_NRT')
#     df = pd.DataFrame({
#             'tracebacks_inference':tracebacks_inference,
#             'session_ids_inference':session_ids_inference,
#             'service_inference':service_inference
#     })
#     return df
   
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


