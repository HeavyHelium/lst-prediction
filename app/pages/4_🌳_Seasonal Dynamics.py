import streamlit as st
import pandas as pd
import plotly.express as plotly
import plotly.graph_objects as go
import plotly.express 

from helper import display_logo




display_logo()

st.markdown("### Indices Correlations <a name='correlation-indices'></a>", unsafe_allow_html=True)

color_scale = plotly.colors.diverging.Picnic



def display_correlation(season=None):
    correlation_data = pd.read_csv("./stats/correlation_matrix_all_seasons.csv", index_col=0)
    if season is not None:
        correlation_data = pd.read_csv(f"./stats/correlation_matrix_{season}.csv", index_col=0)
    else: 
        season = "all seasons"
    fig = plotly.express.imshow(
        correlation_data, 
        title=f"{season.capitalize()} Correlation Matrix",
        color_continuous_scale=color_scale, 
        aspect="equal",
        text_auto='.2f'  # Annotate each square with the value, formatted to 2 decimal places
    )
        # fig.update_layout(
        #     title_font_size=20, 
        #     xaxis_title_font_size=16,
        #     yaxis_title_font_size=16,
        #     coloraxis_colorbar=dict(
        #         title="Correlation",
        #         title_font_size=16,
        #         tickfont_size=14
        #     ),
        #     annotations=[
        #         dict(
        #             text=f"{val:.2f}",
        #             x=col,
        #             y=row,
        #             #font=dict(size=14), 
        #             showarrow=False
        #         )
        #         for row, col, val in zip(correlation_data.index, correlation_data.columns, correlation_data.values.flatten())
        #     ]
        # )
   
    st.plotly_chart(fig)

with st.expander("Autumn Correlation Matrix"):
    display_correlation("autumn")

with st.expander("Spring Correlation Matrix"):
    display_correlation("spring")

with st.expander("Summer Correlation Matrix"):
    display_correlation("summer")

with st.expander("Winter Correlation Matrix"):
    display_correlation("winter")

display_correlation()

st.markdown("### Seasonal Dynamics <a name='dynamics-indices'></a>", unsafe_allow_html=True)

season = st.selectbox("Select a season", ["Spring", "Summer", "Autumn", "Winter"])

@st.cache_data
def load_season_data(season):
    lst_stats = pd.read_csv("./stats/lst_stats_by_year.csv")
    lst_stats.rename(columns={'Unnamed: 0': 'year'}, inplace=True)
    lst_stats.set_index('year', inplace=True)
    season_data = lst_stats[season.lower()].dropna().reset_index()
    return season_data

season_data = load_season_data(season)
# st.write(f"Selected season: {season}")
# st.write(season_data)
# Plot mean LST per year for all seasons
lst_stats = pd.read_csv("./stats/lst_stats_by_year.csv")
lst_stats.rename(columns={'Unnamed: 0': 'year'}, inplace=True)
lst_stats.set_index('year', inplace=True)

# Calculate the mean LST per year across all seasons
mean_lst_per_year = lst_stats.mean(axis=1).reset_index()
mean_lst_per_year.columns = ['year', 'mean_lst']

fig = plotly.express.bar(season_data, x="year", y=season.lower(), title=f"LST Stats for {season} Season")
st.plotly_chart(fig)

fig = plotly.express.bar(mean_lst_per_year, x='year', y='mean_lst', title="Mean LST per Year")
st.plotly_chart(fig)
