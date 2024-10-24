import streamlit as st
import pandas as pd
import plotly.express


from helper import display_logo


display_logo()

st.markdown("## Population data <a name='population-data'></a>", unsafe_allow_html=True)
st.write("Population is obtained from the GHS-POP - R2023A dataset") 

with st.expander("Population stats dataframe"):
    population_stats = pd.read_json("../stats/population_stats.json")
    st.dataframe(population_stats)

column_to_plot = st.selectbox("Select a column to plot", population_stats.columns, index=population_stats.columns.get_loc('sum'))

fig = plotly.express.line(population_stats, x="year", y=column_to_plot, title=f"Population in Sofia, Bulgaria ({column_to_plot})")
st.plotly_chart(fig)