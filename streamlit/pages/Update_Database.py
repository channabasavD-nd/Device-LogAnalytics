# import sys
# import streamlit as st
# import threading
# from db import data_exists 
# sys.path.append('..')
# from lib import mongodb
# from utils import download_logs
# import subprocess
# from session_cronology_analysis import Session_details
# # env,date,devicetype

# upload_lock = threading.Lock()

# st.markdown("<h1 style='text-align: center; color: white;'>Extract Log Analytics</h1>", unsafe_allow_html=True)

# deviceID = st.text_input('Enter Device ID')
# env = st.selectbox("Select Environment", ['Staging','Production']).lower()
# date = st.date_input('Enter Date')  
# device_type = st.selectbox("Select Device Type", ['DTS', 'Normal'])
# date = date.strftime('%Y-%m-%d')
# # st.warning("Make Sure AWS SSO Authentication is completed")

# details = {}
# details['deviceid'] = deviceID
# details['env'] = env
# details['date'] = date
# details['deviceType'] = device_type
# if st.button('Extract'):
#     if upload_lock.locked():
#         st.warning("Another user is already uploading data. Please wait until the upload is complete.")
#     else:
#         exists = data_exists(details) 
#         upload_lock.acquire()
#         try:
#             if not exists:
#                 with st.status("Updating Data...", expanded=True) as status:
#                     try:
                        
#                         outdir = download_logs.download(details)
#                         st.write('downloaded logs')
        
#                         e_status  = download_logs.extract_and_combine_logs(outdir)
#                         st.write('extracted logs')
        
#                         # outdir = '3633090953/2024-03-13'
#                         session_obj = Session_details(outdir, details)
#                         for attribute_name, attribute_value in vars(Session_details).items():
#                             if callable(attribute_value) and attribute_name != "__init__":
#                                     attribute_value(session_obj)
#                         # st.write(session_obj.session_ids)
#                         mongodb.populate_db(session_obj.session_ids)
#                         mongodb.update_tracebacks(session_obj.tracebacks)
        
        
#                     except Exception as e:
#                         st.error(e)
#                         st.error('Try again with valid details')
#                         status.update(label="Update Failed!", state="error", expanded=True)
#                         st.stop()
        
#                     status.update(label="Successfully updated!", state="complete", expanded=False)
#                 st.success("Data successfully updated")
#             else:
#                  st.info('Data already exists')
#         finally:
#             upload_lock.release()

import sys
import streamlit as st
import threading
from db import data_exists 
sys.path.append('..')
from lib import mongodb
from utils import download_logs
import subprocess
from session_cronology_analysis import Session_details

upload_lock = threading.Lock()

st.markdown("<h1 style='text-align: center; color: white;'>Extract Log Analytics</h1>", unsafe_allow_html=True)

deviceID = st.text_input('Enter Device ID')
env = st.selectbox("Select Environment", ['Staging','Production']).lower()
date = st.date_input('Enter Date')  
device_type = st.selectbox("Select Device Type", ['DTS', 'Normal'])
date = date.strftime('%Y-%m-%d')

details = {}
details['deviceid'] = deviceID
details['env'] = env
details['date'] = date
details['deviceType'] = device_type

if upload_lock.locked():
    st.warning("Another user is already uploading data. Please wait until the upload is complete.")
else:
    if st.button('Extract'):
        exists = data_exists(details) 
        if not exists:
            with upload_lock:
                with st.status("Updating Data...", expanded=True) as status:
                    try:
                        outdir = download_logs.download(details)
                        st.write('downloaded logs')
        
                        e_status  = download_logs.extract_and_combine_logs(outdir)
                        st.write('extracted logs')
        
                        session_obj = Session_details(outdir, details)
                        for attribute_name, attribute_value in vars(Session_details).items():
                            if callable(attribute_value) and attribute_name != "__init__":
                                attribute_value(session_obj)
                        mongodb.populate_db(session_obj.session_ids)
                        mongodb.update_tracebacks(session_obj.tracebacks)
                    except Exception as e:
                        st.error(e)
                        st.error('Try again with valid details')
                        status.update(label="Update Failed!", state="error", expanded=True)
                        st.stop()
                    finally:
                        upload_lock.release()
                    status.update(label="Successfully updated!", state="complete", expanded=False)
            st.success("Data successfully updated")
        else:
            st.info('Data already exists')

    
