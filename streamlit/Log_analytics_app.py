import streamlit as st  
from generate_report import gen_report
from dashboard import display_dashboard  
from db import get_data, getAllCollections, get_tracebacks

image_url = 'data:image/png;base64,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'
st.set_page_config(page_title = "Analytics Dashboard", page_icon=image_url, layout="wide", initial_sidebar_state="auto", menu_items=None)
st.markdown("<h1 style='text-align: center; color: white;'>Device-log Analytics</h1>", unsafe_allow_html=True)
def main():  

    device_ids = getAllCollections()
    deviceID = st.selectbox('Enter Device ID', device_ids.keys()) 
    ota_version = st.selectbox('Enter OTA Version', device_ids[deviceID])  
    date = st.date_input('Enter Date')  
    st.session_state['deviceID'] = deviceID
    st.session_state['ota_version'] = ota_version
    st.session_state['date'] = date
    if st.button('Get Data'): 
        documents = get_data()  
        report = display_dashboard(documents)  
        tracebacks = get_tracebacks()
        gen_report(report,tracebacks)  
    
  
if __name__ == "__main__":  
    main()  



# NOTE: review logs to extract some more useful info (*)
# check for standards(sonarcube)(*)
# add cache
# make report readable 
# add initialization to ini file (*)
# create dashboard for presentation
# add multiple days feature(*)(for atleast analytics)
# Test it on various devious(DTS/Normal) (staging/production)(**)


# add loggers to all files(for streamlit refer github)(**)
# deploy on my EC2 instance
# after updating - delete the logs
# Add dates that are available(mayb as a info message)
# handle session states of multiple pages


#status on PR raised
#deploy
#complete the excel
#Arpan's task 
#testing D215
#modify the code 
