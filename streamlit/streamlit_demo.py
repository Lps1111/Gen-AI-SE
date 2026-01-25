import streamlit as st

st.title('my first streamlit app')
Name= st.text_input('Enter your name')
if st.button('say hello'):
    if Name:
        st.success(f"hello{Name},welcome")
    else:
        st.warning("waht is your name")

