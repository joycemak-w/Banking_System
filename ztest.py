# import streamlit as st
# import time

# # Initialize session state
# if 'running' not in st.session_state:
#     st.session_state.running = False

# # Create a placeholder for the current time
# time_placeholder = st.empty()

# # Button to start updating time
# if st.button("Start Updating Time"):
#     st.session_state.running = True

# # Button to stop updating time
# if st.button("Stop Updating"):
#     st.session_state.running = False

# # Update the time every second if running
# if st.session_state.running:
#     while st.session_state.running:
#         current_time = time.strftime("%H:%M:%S")
#         time_placeholder.text(f"Current Time: {current_time}")
#         time.sleep(60)  # Wait for 1 second
#         # Refresh the app state
#         st.rerun()

# # Display the initial time or last updated time
# if not st.session_state.running:
#     time_placeholder.text(f"Current Time: {time.strftime('%H:%M:%S')}")

# # Other components remain functional
# st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"])

import streamlit as st
import time

# Create a placeholder for the current time
time_placeholder = st.empty()

# Create a selectbox
s = st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"])
st.write(s)

# Update the time every second
while True:
    current_time = time.strftime("%H:%M:%S")
    time_placeholder.text(f"Current Time: {current_time}")
    time.sleep(60)  # Wait for 1 second