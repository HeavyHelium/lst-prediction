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
from streamlit_folium import folium_static

import plotly.express

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
]]);

# Define urban and rural polygons
Urban = ee.Geometry.MultiPolygon(
        [[[[23.246904788408127, 42.688226341159925],
           [23.323809085283127, 42.65339079664303],
           [23.359514651689377, 42.69882458798372],
           [23.310076175126877, 42.71951119054903],
           [23.271624026689377, 42.71143919029933]]],
         [[[23.255144534501877, 42.74170377728034],
           [23.243471560869065, 42.710934655422136],
           [23.281923709306565, 42.71698880325915],
           [23.282610354814377, 42.72859093579189]]],
         [[[23.380114016923752, 42.70437532879963],
           [23.383547244462815, 42.674597366330666],
           [23.426805911455002, 42.6917592910562],
           [23.41787951985344, 42.7033661401078]]]])

Rural = ee.Geometry.MultiPolygon(
        [[[[23.46457141438469, 42.666771974480405],
           [23.469377932939377, 42.64657286301201],
           [23.49306720295891, 42.65869311722898],
           [23.481737552080002, 42.671568299263335]]],
         [[[23.254394538400174, 42.64365931309603],
           [23.258857734200955, 42.627241935261246],
           [23.282032020089627, 42.635830026978525],
           [23.267784125802518, 42.64530081266675]]]]);

logo = Image.open("./img/logo.png")
st.sidebar.image(logo, width=200)

st.sidebar.title("Content")
st.sidebar.markdown("---")
st.sidebar.markdown("[Title](#main-title)")
st.sidebar.markdown("[Area of Interest](#area-of-interest)")
st.sidebar.markdown("[Population Data Analysis](#population-data)")
st.sidebar.markdown("[Remote Sensing Data](#remote-sensing-data)")
st.sidebar.markdown("[Urban Heat Island Mapping](#urban-heat-island-mapping)")
st.sidebar.markdown("[Machine Learning Training](#machine-learning-training)")
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This application analyzes the SUHI effect in Sofia, Bulgaria, integrating remote-sensing imagery and socioeconomic data.")

st.markdown("# The SUHI effect in Sofia, Bulgaria <a name='main-title'></a>", unsafe_allow_html=True)
st.markdown("## An analysis based on the integration of remote-sensing imagery and socioeconomic data <a name='sub-title'></a>", unsafe_allow_html=True)
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

st.markdown("### Population data <a name='population-data'></a>", unsafe_allow_html=True)
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

    landsat_image = ee.Image(f"LANDSAT/{ls_collection}/C02/{tier}_L2/{image_id}").preprocess().clip(aoiZoomed)
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
        opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.6)

    folium_map = folium.Map(location=[42.7133, 23.3469], zoom_start=10) 

    folium.GeoJson(Urban.getInfo(), name="Urban Areas", style_function=lambda x: {'color': 'green'}).add_to(folium_map)
    folium.GeoJson(Rural.getInfo(), name="Rural Areas", style_function=lambda x: {'color': 'yellow'}).add_to(folium_map)

    st_band_url = st_band.getThumbURL({
        'min': min_value,
        'max': max_value,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    })
    folium.raster_layers.ImageOverlay(
        image=st_band_url,
        bounds=[[42.591241793466885, 23.147785867237445], [42.83542772358794, 23.546040261768695]],
        opacity=opacity
    ).add_to(folium_map)

    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    folium_static(folium_map)

map_plot(selected_image_id)



st.markdown("### Machine Learning training <a name='machine-learning-training'></a>", unsafe_allow_html=True)
# Select algorithm
algorithm = st.selectbox("Choose an algorithm", ("Linear Regression", "Random Forest"))

# Load dataset for training
data = pd.read_csv("data/training_data.csv")
X = data.drop(columns=["target"])
y = data["target"]

# Train and validate model
if st.button("Run Model"):
    def get_linear_regression_model():
        return LinearRegression()

    def get_random_forest_model():
        return RandomForestRegressor()

    model_mapping = {
        "Linear Regression": get_linear_regression_model,
        "Random Forest": get_random_forest_model
    }

    model = model_mapping[algorithm]()

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Validate the model
    predictions = model.predict(X_val)
    mse = mean_squared_error(y_val, predictions)

    st.write(f"Mean Squared Error: {mse}")

    # Plot predictions vs actual values
    fig, ax = plt.subplots()
    ax.scatter(y_val, predictions)
    ax.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'k--', lw=2)
    ax.set_xlabel('Actual')
    ax.set_ylabel('Predicted')
    ax.set_title(f'{algorithm} Predictions vs Actual')
    st.pyplot(fig)