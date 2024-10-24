import streamlit as st

def display_logo(home=False):
    path = "./img/logo.png"
    # if not home: 
    #     path = "./" + path

    st.sidebar.image("./img/logo.png", width=150)
    st.sidebar.info("This application analyzes the SUHI effect in Sofia, Bulgaria, \
                     integrating remote-sensing imagery and socioeconomic data.")
