import streamlit as st
import pandas as pd
import ee
import eemont
import geemap.foliumap as geemap
import folium
import plotly
import plotly.express as px


from streamlit_folium import folium_static
from folium import plugins
import branca.colormap as cm



from helper import display_logo

display_logo()


aoi_larger = st.session_state['aoi_larger']
urbanBuildings = st.session_state['urbanBuildings']
urbanWater = st.session_state['urbanWater']
RuralOther = st.session_state['RuralOther']
UrbanPark = st.session_state['UrbanPark']
geojson_layers = st.session_state['geojson_layers']



st.markdown("## Remote Sensing Data <a name='remote-sensing-data'></a>", unsafe_allow_html=True)
st.markdown("### Urban Heat Island Mapping <a name='urban-heat-island-mapping'></a>", unsafe_allow_html=True)
id_list = st.session_state['id_list']
id_list_full = st.session_state['id_list_full']



def get_mean_lst(image, geometry, band_name):
            st_band = image.select(band_name).subtract(273.15)
            mean_lst = st_band.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=30,
                bestEffort=True
            ).get(band_name).getInfo()
            return mean_lst


def get_landsat_image(selected_image_id, aoi_larger):
    ls_collection = selected_image_id.split('_')[0]
    st_band_name = 'ST_B6' if ls_collection in ['LE07', 'LT05', 'LT04'] else 'ST_B10'
    tier = id_list_full[selected_image_id]['tier']
    image = ee.Image(f"LANDSAT/{ls_collection}/C02/{tier}_L2/{selected_image_id}").preprocess().clip(aoi_larger)
    st.session_state['landsat_image'] = image
    st.session_state['st_band_name'] = st_band_name

    st.session_state['selected_image_id'] = selected_image_id
    st.session_state['mean_lst_urban_water'] = get_mean_lst(image, urbanWater, st_band_name)
    st.session_state['mean_lst_rural_other'] = get_mean_lst(image, RuralOther, st_band_name)
    st.session_state['mean_lst_urban_park'] = get_mean_lst(image, UrbanPark, st_band_name)
    st.session_state['mean_lst_urban_buildings'] = get_mean_lst(image, urbanBuildings, st_band_name)
    print("Image loaded")
    st.write("Image loaded")

selected_image_id = st.selectbox("Select an Image ID", id_list, index=6)


image_changed = False 
if st.session_state.get('selected_image_id') is None:
    image_changed = True
    get_landsat_image(selected_image_id, aoi_larger)
elif st.session_state.get('selected_image_id') != selected_image_id:
    image_changed = True
    get_landsat_image(selected_image_id, aoi_larger)


landsat_image, st_band_name = st.session_state['landsat_image'], st.session_state['st_band_name']


def map_plot(image: ee.Image):
    st_band = image.select(st_band_name).subtract(273.15)

    mean_urban = st.session_state.get('mean_lst_urban_buildings')
    mean_rural = st.session_state.get('mean_lst_rural_other')

    minv, maxv = min(mean_urban, mean_rural), max(mean_urban, mean_rural)
    vis_params = {
        'min': mean_rural,  
        'max': mean_urban,  
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red'],
    }

    temperature_difference = mean_urban - mean_rural
    st.metric(label="Temperature Difference (Sample Buildings - Sample Rural)", value=f"{temperature_difference:.2f} °C")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        min_value = st.number_input("Custom min value", value=minv, format="%.2f")
    with col2:
        max_value = st.number_input("Custom max value", value=maxv, format="%.2f")
    with col3:
        opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.3)

    folium_map = geemap.Map(location=[42.7133, 23.3469], zoom_start=10, tiles=None, control_scale=False) 

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

    colormap = cm.LinearColormap(
        colors=['blue', 'cyan', 'yellow', 'orange', 'red'],
        vmin=min_value,
        vmax=max_value,
        caption='Surface Temperature (°C)'
    )
    folium.TileLayer("", name="None", attr="blank").add_to(folium_map)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(folium_map)
    colormap.add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    folium_static(folium_map)


def plot_difference_charts(image: ee.Image):
    with st.expander("LST Comparison Of Selected Regions"):
        
        mean_lst_urban_water = st.session_state['mean_lst_urban_water']
        mean_lst_rural_other = st.session_state['mean_lst_rural_other']
        mean_lst_urban_park = st.session_state['mean_lst_urban_park']
        mean_lst_urban_buildings = st.session_state['mean_lst_urban_buildings']
        
        data = {
            "Area": [geojson_layers["urbanWater"][0], geojson_layers["RuralOther"][0], geojson_layers["UrbanPark"][0], geojson_layers["urbanBuildings"][0]],
            "Mean LST (°C)": [mean_lst_urban_water, mean_lst_rural_other, mean_lst_urban_park, mean_lst_urban_buildings],
            "Color": [geojson_layers["urbanWater"][1], geojson_layers["RuralOther"][1], geojson_layers["UrbanPark"][1], geojson_layers["urbanBuildings"][1]]
        }
        df = pd.DataFrame(data)
        fig = plotly.express.bar(df, x="Area", y="Mean LST (°C)", title=f"Mean LST for Different Areas ({selected_image_id})", color="Area", color_discrete_map=dict(zip(data["Area"], data["Color"])))
        st.plotly_chart(fig)
        
        df = df.reset_index(drop=True)
        st.dataframe(df[["Area", "Mean LST (°C)"]])
    
plot_difference_charts(landsat_image)
map_plot(landsat_image)

