import streamlit as st

st.title("Test App")
st.write("Hello, this is a test!")

# Add a simple input
user_input = st.text_input("Enter your name")
if user_input:
    st.write(f"Hello, {user_input}!")
