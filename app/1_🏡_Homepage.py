import ee
import streamlit as st
import geopandas as gpd
import plotly.express
import pandas as pd
import google.auth

from helper import display_logo


def initialize():
  # try:
    ee.Authenticate()
    ee.Initialize(project="ee-dianamarkovakn")
    # except ee.EEException:
    #     ee.Authenticate()
    #     ee.Initialize()
    #google.auth.default()

    aoiZoomed = ee.Geometry.Polygon([
        [ [23.147785867237445, 42.591241793466885],
          [23.546040261768695, 42.591241793466885],
          [23.546040261768695, 42.83542772358794],
          [23.147785867237445, 42.83542772358794],
        ]
    ])

    st.session_state['id_list'] = pd.read_json("../data/id_list.json")["id"].tolist()
    st.session_state['id_list_full'] = pd.read_json("../data/id_list.json").set_index("id").to_dict(orient="index")

    coords = aoiZoomed.bounds().coordinates().getInfo()[0]
    top_left = coords[0]
    bottom_right = coords[2]

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
          [23.730061257862445, 42.9219731159366]]])

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
           [23.267784125802518, 42.64530081266675]]]])

    urbanBuildings = ee.Geometry.Polygon(
        [[[23.319328806750036, 42.69842760252894],
          [23.319328806750036, 42.69611599160914],
          [23.322438806750036, 42.69611599160914],
          [23.322438806750036, 42.69842760252894]]])

    urbanWater = ee.Geometry.Polygon(
        [[[23.39812287739303, 42.66429802169629],
          [23.39812287739303, 42.661986410776485],
          [23.40123287739303, 42.661986410776485],
          [23.40123287739303, 42.66429802169629]]])

    RuralOther = ee.Geometry.Polygon(
        [[[23.33460979617574, 42.76828619219489],
          [23.33460979617574, 42.765974581275085],
          [23.33771979617574, 42.765974581275085],
          [23.33771979617574, 42.76828619219489]]])

    UrbanPark = ee.Geometry.Polygon(
        [[[23.335287603416116, 42.68720648908851],
          [23.335287603416116, 42.68489487816871],
          [23.338397603416116, 42.68489487816871],
          [23.338397603416116, 42.68720648908851]]])

    # Store variables in session state
    st.session_state['aoiZoomed'] = aoiZoomed
    st.session_state['top_left'] = top_left
    st.session_state['bottom_right'] = bottom_right
    st.session_state['geojson_layers'] = geojson_layers
    st.session_state['aoi_larger'] = aoi_larger
    st.session_state['Urban'] = Urban
    st.session_state['Rural'] = Rural
    st.session_state['urbanBuildings'] = urbanBuildings
    st.session_state['urbanWater'] = urbanWater
    st.session_state['RuralOther'] = RuralOther
    st.session_state['UrbanPark'] = UrbanPark
    st.session_state['aoi-larger'] = aoi_larger
    st.session_state['Initialized'] = True




if 'Initialized' not in st.session_state:
    initialize()
    st.rerun() 


display_logo(home=True)


st.markdown("# The SUHI effect in Sofia, Bulgaria <a name='main-title'></a>", unsafe_allow_html=True)
st.markdown("## Analysis based on the integration of remote-sensing imagery and socioeconomic data <a name='sub-title'></a>", unsafe_allow_html=True)
st.caption("by Diana Markova, mentored by Dr. Lidia Vitanova and Prof. Dessislava Petrova-Antonova")

st.markdown("### Area of interest <a name='area-of-interest'></a>", unsafe_allow_html=True)
geojson_file = "../shapefiles/sofia-boundaries.json"
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
fig.update_coloraxes(showscale=False)  
st.plotly_chart(fig)