# Import Streamlit  
import streamlit as st  
  
# Title of the app  
st.title("Simple Streamlit App")  
  
# User input  
user_input = st.text_input("Enter your name:")  
  
# Display the user input  
st.write("Hello, {}!".format(user_input))  
