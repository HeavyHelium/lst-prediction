import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly 
import geopandas as gpd
import geemap
import eemont
import ee
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from PIL import Image
import folium
import folium.plugins
import branca.colormap as cm
from streamlit_folium import folium_static

import plotly.express

# st.markdown(
#     """
#     <style>
#     /* Increase the font size for the whole app */
#     html, body, label [class*="css"]  {
#         font-size: 20px;
#     }
#     </style>
#     """, unsafe_allow_html=True
# )


# Initialize the Earth Engine library.
try:
    ee.Initialize()
except ee.EEException:
    ee.Authenticate()
    ee.Initialize()

aoiZoomed = ee.Geometry.Polygon([
    [ [23.147785867237445, 42.591241793466885],
      [23.546040261768695, 42.591241793466885],
      [23.546040261768695, 42.83542772358794],
      [23.147785867237445, 42.83542772358794],
    ]
])

# Get the coordinates of the top left and bottom right points
coords = aoiZoomed.bounds().coordinates().getInfo()[0]
top_left = coords[0]
bottom_right = coords[2]

# print("Top Left:", top_left)
# print("Bottom Right:", bottom_right)


geojson_layers = {
    "urbanWater": ("Sample Water - Druzhba reservoir", 'blue'),
    "RuralOther": ("Sample Rural North", 'brown'),
    "UrbanPark": ("Sample Park - Borisova gradina", 'green'),
    "urbanBuildings": ("Sample Buildings - St. Nedelya Square", 'red')
}

aoi_larger = ee.Geometry.Polygon(
    [[[23.054402078174945, 42.9219731159366],
      [23.054402078174945, 42.39885249302785],
      [23.730061257862445, 42.39885249302785],
      [23.730061257862445, 42.9219731159366]]]);


# Define urban and rural polygons
Urban = ee.Geometry.MultiPolygon(
        [[[[23.28930500030052, 42.683309305605796],
           [23.3311895761537, 42.687217844774736],
           [23.332563262800576, 42.69756705054173],
           [23.32724298122744, 42.70866708276199],
           [23.31642747207472, 42.71749663916301],
           [23.28467106424651, 42.70967714251649],
           [23.278062132579702, 42.69788103123934]]],
         [[[23.255144534501877, 42.74170377728034],
           [23.234201846513596, 42.714718567030864],
           [23.255659518632736, 42.707528937725925],
           [23.280207095537033, 42.722285698139146]]],
         [[[23.313479223100213, 42.723112430622024],
           [23.32429388984826, 42.71794172644094],
           [23.331160344926385, 42.734965589318975],
           [23.320002355424432, 42.743286666368654]]],
         [[[23.39190308440334, 42.701886292625346],
           [23.389843411874686, 42.69242360863146],
           [23.406666796562945, 42.689144709426664],
           [23.427610437989152, 42.69368552947923],
           [23.439583881040793, 42.693181107063346],
           [23.441772694684165, 42.69507373663753],
           [23.416280655376184, 42.6978491269261]]]])

Rural = ee.Geometry.MultiPolygon(
        [[[[23.46457141438469, 42.666771974480405],
           [23.469377932939377, 42.64657286301201],
           [23.49306720295891, 42.65869311722898],
           [23.481737552080002, 42.671568299263335]]],
         [[[23.254394538400174, 42.64365931309603],
           [23.258857734200955, 42.627241935261246],
           [23.282032020089627, 42.635830026978525],
           [23.267784125802518, 42.64530081266675]]]]);


urbanBuildings = ee.Geometry.Polygon(
    [[[23.319328806750036, 42.69842760252894],
      [23.319328806750036, 42.69611599160914],
      [23.322438806750036, 42.69611599160914],
      [23.322438806750036, 42.69842760252894]]], None, False)

urbanWater = ee.Geometry.Polygon(
    [[[23.39812287739303, 42.66429802169629],
      [23.39812287739303, 42.661986410776485],
      [23.40123287739303, 42.661986410776485],
      [23.40123287739303, 42.66429802169629]]], None, False)

RuralOther = ee.Geometry.Polygon(
    [[[23.33460979617574, 42.76828619219489],
      [23.33460979617574, 42.765974581275085],
      [23.33771979617574, 42.765974581275085],
      [23.33771979617574, 42.76828619219489]]], None, False)

UrbanPark = ee.Geometry.Polygon(
    [[[23.335287603416116, 42.68720648908851],
      [23.335287603416116, 42.68489487816871],
      [23.338397603416116, 42.68489487816871],
      [23.338397603416116, 42.68720648908851]]], None, False)





logo = Image.open("./img/logo.png")
st.sidebar.image(logo, width=200)

st.sidebar.title("Content")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<ul>
    <li><a href="#main-title">Topic</a></li>
    <li><a href="#area-of-interest">Area of Interest</a>
        <ul>
            <li><a href="#population-data">Population Data Analysis</a></li>
            <li><a href="#remote-sensing-data">Remote Sensing Data</a>
                <ul>
                    <li><a href="#urban-heat-island-mapping">Urban Heat Island Mapping</a></li>
                    <li><a href="#correlation-indices">Indices Correlations</a></li>
                    <li><a href="#dynamics-indices">Seasonal Dynamics</a></li>
                </ul>
            </li>
        </ul>
    </li>
    <li><a href="#machine-learning-training">Machine Learning Regression</a></li>
</ul>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This application analyzes the SUHI effect in Sofia, Bulgaria, integrating remote-sensing imagery and socioeconomic data.")

st.markdown("# The SUHI effect in Sofia, Bulgaria <a name='main-title'></a>", unsafe_allow_html=True)
st.markdown("## Analysis based on the integration of remote-sensing imagery and socioeconomic data <a name='sub-title'></a>", unsafe_allow_html=True)
st.caption("by Diana Markova, mentored by Dr. Lidia Vitanova and Prof. Dessislava Petrova-Antonova")

st.markdown("### Area of interest <a name='area-of-interest'></a>", unsafe_allow_html=True)
geojson_file = "shapefiles/sofia-boundaries.json"
gdf = gpd.read_file(geojson_file)

fig = plotly.express.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color=gdf.index,
    title="Sofia-city municipality",
    mapbox_style="open-street-map",  
    center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()},
    zoom=4
)
fig.update_layout(
    mapbox_zoom=7, 
    mapbox_center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()},
    title={
        'text': "Sofia-city municipality",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}
    }
)
fig.update_coloraxes(showscale=False)  # Hide the index scale
st.plotly_chart(fig)

st.markdown("## Population data <a name='population-data'></a>", unsafe_allow_html=True)
st.write("Population is obtained from the GHS-POP - R2023A dataset") 

with st.expander("Population stats dataframe"):
    population_stats = pd.read_json("stats/population_stats.json")
    st.dataframe(population_stats)

column_to_plot = st.selectbox("Select a column to plot", population_stats.columns, index=population_stats.columns.get_loc('sum'))

fig = plotly.express.line(population_stats, x="year", y=column_to_plot, title=f"Population in Sofia, Bulgaria ({column_to_plot})")
st.plotly_chart(fig)

st.markdown("## Remote Sensing Data <a name='remote-sensing-data'></a>", unsafe_allow_html=True)
st.markdown("### Urban Heat Island Mapping <a name='urban-heat-island-mapping'></a>", unsafe_allow_html=True)
id_list = pd.read_json("data/id_list.json")["id"].tolist()
id_list_full = pd.read_json("data/id_list.json").set_index("id").to_dict(orient="index")
print(id_list_full)

selected_image_id = st.selectbox("Select an Image ID", id_list)
def map_plot(image_id: str):
    ls_collection = image_id.split('_')[0]
    st_band_name = 'ST_B6' if ls_collection in ['LE07', 'LT05', 'LT04'] else 'ST_B10'
    tier = id_list_full[image_id]['tier']

    landsat_image = ee.Image(f"LANDSAT/{ls_collection}/C02/{tier}_L2/{image_id}").preprocess().clip(aoi_larger)
    st_band = landsat_image.select(st_band_name).subtract(273.15)

    mean_urban = st_band.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=Urban,
        scale=30,
        bestEffort=True
    ).get(st_band_name).getInfo()

    mean_rural = st_band.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=Rural,
        scale=30,
        bestEffort=True
    ).get(st_band_name).getInfo()

    vis_params = {
        'min': mean_rural,  
        'max': mean_urban,  
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red'],
    }

    st.write("Mean Surface Temperature in Urban Areas:", f"{mean_urban:.2f}")
    st.write("Mean Surface Temperature in Rural Areas:", f"{mean_rural:.2f}")
  
    temperature_difference = mean_urban - mean_rural
    st.metric(label="Temperature Difference (Urban - Rural)", value=f"{temperature_difference:.2f} °C")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        min_value = st.number_input("Custom min value", value=mean_rural, format="%.2f")
    with col2:
        max_value = st.number_input("Custom max value", value=mean_urban, format="%.2f")
    with col3:
        opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.3)

    min_value, max_value = min(min_value, max_value), max(min_value, max_value)

    folium_map = folium.Map(location=[42.7133, 23.3469], zoom_start=10) 

    folium.GeoJson(Urban.getInfo(), name="Urban Areas", style_function=lambda x: {'color': 'red'}).add_to(folium_map)
    folium.GeoJson(Rural.getInfo(), name="Rural Areas", style_function=lambda x: {'color': 'yellow'}).add_to(folium_map)


    for variable_name, (layer_name, color) in geojson_layers.items():
        variable = globals()[variable_name]
        folium.GeoJson(variable.getInfo(), name=layer_name, style_function=lambda x, color=color: {'color': color}).add_to(folium_map)
  

    st_band_url = st_band.getThumbURL({
        'min': min_value,
        'max': max_value,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    })
    folium.raster_layers.ImageOverlay(
        image=st_band_url,
        bounds=[[42.39885249302785, 23.054402078174945], 
                [42.9219731159366, 23.730061257862445]],
        opacity=opacity,
        name="Surface Temperature"
    ).add_to(folium_map)

    # Add color scale
    colormap = cm.LinearColormap(
        colors=['blue', 'cyan', 'yellow', 'orange', 'red'],
        vmin=min_value,
        vmax=max_value,
        caption='Surface Temperature (°C)'
    )
    colormap.add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    folium_static(folium_map)

map_plot(selected_image_id)

def plot_difference_charts(selected_image_id):
    with st.expander("LST Comparison Of Selected Regions"):
        def get_mean_lst(image_id, geometry, band_name):
            ls_collection = image_id.split('_')[0]
            tier = id_list_full[image_id]['tier']
            landsat_image = ee.Image(f"LANDSAT/{ls_collection}/C02/{tier}_L2/{image_id}").preprocess().clip(aoi_larger)
            st_band = landsat_image.select(band_name).subtract(273.15)
            mean_lst = st_band.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=30,
                bestEffort=True
            ).get(band_name).getInfo()
            return mean_lst

        st_band_name = 'ST_B6' if selected_image_id.split('_')[0] in ['LE07', 'LT05', 'LT04'] else 'ST_B10'
        
        mean_lst_urban_water = get_mean_lst(selected_image_id, urbanWater, st_band_name)
        mean_lst_rural_other = get_mean_lst(selected_image_id, RuralOther, st_band_name)
        mean_lst_urban_park = get_mean_lst(selected_image_id, UrbanPark, st_band_name)
        mean_lst_urban_buildings = get_mean_lst(selected_image_id, urbanBuildings, st_band_name)

        temperature_difference = mean_lst_urban_buildings - mean_lst_rural_other
        st.metric(label="Temperature Difference (Sample Buildings - Sample Rural)", value=f"{temperature_difference:.2f} °C")

        
        data = {
            "Area": [geojson_layers["urbanWater"][0], geojson_layers["RuralOther"][0], geojson_layers["UrbanPark"][0], geojson_layers["urbanBuildings"][0]],
            "Mean LST (°C)": [mean_lst_urban_water, mean_lst_rural_other, mean_lst_urban_park, mean_lst_urban_buildings]
        }
        df = pd.DataFrame(data)
        fig = plotly.express.bar(df, x="Area", y="Mean LST (°C)", title=f"Mean LST for Different Areas ({selected_image_id})")
        st.plotly_chart(fig)
        
        df = df.reset_index(drop=True)
        st.dataframe(df[["Area", "Mean LST (°C)"]])
        
    
plot_difference_charts(selected_image_id)

st.markdown("### Indices Correlations <a name='correlation-indices'></a>", unsafe_allow_html=True)


def display_correlation(season=None):
    if season is not None:
        correlation_data = pd.read_csv(f"stats/correlation_matrix_{season}.csv", index_col=0)
        fig = plotly.express.imshow(
            correlation_data, 
            title=f"{season.capitalize()} Correlation Matrix",
            color_continuous_scale='PuOr', 
            aspect="equal"  
        )
        fig.update_layout(
            title_font_size=20, 
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            coloraxis_colorbar=dict(
                title="Correlation",
                title_font_size=16,
                tickfont_size=14
            )
        )
        st.plotly_chart(fig)
    else: 
        # we load the correlation_matrix_all_seasons.csv
        correlation_data = pd.read_csv("stats/correlation_matrix_all_seasons.csv", index_col=0)
        fig = plotly.express.imshow(
            correlation_data, 
            title="All Seasons Correlation Matrix",
            color_continuous_scale='PuOr', 
            aspect="equal"  
        )
        fig.update_layout(
            title_font_size=20, 
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            coloraxis_colorbar=dict(
                title="Correlation",
                title_font_size=16,
                tickfont_size=14
            )
        )
        st.plotly_chart(fig)

col1, col2 = st.columns(2)
with col1:
    display_correlation("autumn")
with col2:
    display_correlation("spring")

col3, col4 = st.columns(2)
with col3:
    display_correlation("summer")
with col4:
    display_correlation("winter")

display_correlation()

st.markdown("### Seasonal Dynamics <a name='dynamics-indices'></a>", unsafe_allow_html=True)

season = st.selectbox("Select a season", ["Spring", "Summer", "Autumn", "Winter"])

@st.cache_data
def load_season_data(season):
    lst_stats = pd.read_csv("stats/lst_stats_by_year.csv")
    lst_stats.rename(columns={'Unnamed: 0': 'year'}, inplace=True)
    lst_stats.set_index('year', inplace=True)
    season_data = lst_stats[season.lower()].dropna().reset_index()
    return season_data

season_data = load_season_data(season)
# st.write(f"Selected season: {season}")
# st.write(season_data)

fig = plotly.express.bar(season_data, x="year", y=season.lower(), title=f"LST Stats for {season} Season")
st.plotly_chart(fig)

st.markdown("## Machine Learning Regression <a name='machine-learning-training'></a>", unsafe_allow_html=True)
algorithm = st.selectbox("Choose an algorithm", ("Linear Regression", "Random Forest", "XGBoost", "Multi-layer Perceptron", "Support Vector Machine", "K-Nearest Neighbors"))

# Load dataset for training
# data = pd.read_csv("data/training_data.csv")
# X = data.drop(columns=["target"])
# y = data["target"]

# # Train and validate model
# if st.button("Run Model"):
#     def get_linear_regression_model():
#         return LinearRegression()

#     def get_random_forest_model():
#         return RandomForestRegressor()

#     model_mapping = {
#         "Linear Regression": get_linear_regression_model,
#         "Random Forest": get_random_forest_model
#     }

#     model = model_mapping[algorithm]()

#     # Split data into training and validation sets
#     X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Train the model
#     model.fit(X_train, y_train)

#     # Validate the model
#     predictions = model.predict(X_val)
#     mse = mean_squared_error(y_val, predictions)

#     st.write(f"Mean Squared Error: {mse}")

#     # Plot predictions vs actual values
#     fig, ax = plt.subplots()
#     ax.scatter(y_val, predictions)
#     ax.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'k--', lw=2)
#     ax.set_xlabel('Actual')
#     ax.set_ylabel('Predicted')
#     ax.set_title(f'{algorithm} Predictions vs Actual')
#     st.pyplot(fig)
