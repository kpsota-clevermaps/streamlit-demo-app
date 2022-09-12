"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
from cm_sdk import session, wrappers, dwh


def query_result_to_pd_data(metric_results):

    data = {}
    for mr in metric_results:
        for prop in list(mr['content'].keys()):
            if prop not in data:
                data[prop] = []
            data[prop].append(mr['content'][prop])

    return data


def draw_map():

    if not st.session_state.poi_subtype_selected:
        return

    properties = ['poi_dwh.name', 'poi_dwh.lat', 'poi_dwh.lng']
    filter_by = [
        {
            "property": "poi_dwh.subtype_name",
            "operator": "in",
            "value": st.session_state.poi_subtype_selected
        }
    ]

    query_json = {
        'properties': properties,
        'filter_by': filter_by
    }

    rows_results = wrappers.query(st.session_state.cm_session, query_json, 1000)
    data = query_result_to_pd_data(rows_results)

    df = pd.DataFrame(data=data)
    df = df.rename(columns={'poi_dwh_name': 'name', 'poi_dwh_lng': 'lng', 'poi_dwh_lat': 'lat'})

    st.session_state.map_placeholder = st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=50.0698,
            longitude=14.4037,
            zoom=11,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position=['lng', 'lat'],
                get_color='[200, 30, 0, 160]',
                get_radius=50,
                radius_min_pixels=1,
                radius_max_pixels=100
            )
        ]
    ))

def test():

    st.write('Selected option: {}'.format(st.session_state.poi_subtype_selected))

def main():

    project_id = st.secrets["cm_project_id"]
    dwh_id = st.secrets["cm_dwh_id"]
    access_token = st.secrets["cm_access_token"]
    server_url = "https://secure.clevermaps.io"

    cm_session = session.Session(project_id, dwh_id, access_token, server_url)
    st.session_state.cm_session = cm_session

    # split_properties = ["poi_dwh.type_name"]
    # split_properties = ["orp_dwh.nazev"]
    # metric_results = api_caller.query_metric('pois_sum_metric', properties_names=split_properties)
    # data = query_result_to_pd_data(metric_results)

    st.set_page_config(layout="wide")

    st.title('CleverMaps Demo Data App')

    cm_prop_values = dwh.PropertyValues(cm_session)
    poi_subtypes = cm_prop_values.get_property_values('poi_dwh.subtype_name')

    st.selectbox('Select POI subtype to display', poi_subtypes, index=0, key='poi_subtype_selected')
    #st.multiselect('Select POI subtype to display', poi_subtypes, key='poi_subtype_selected')

    map_placeholder = st.empty()
    st.session_state.map_placeholder = map_placeholder

    draw_map()

    #components.iframe('https://secure.clevermaps.io/#/v40dvff322hpko0e/map/review_view', width=1280, height=720)

    #st.write(st.session_state)



main()
