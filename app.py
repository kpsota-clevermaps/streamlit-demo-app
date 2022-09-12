"""
# Streamlit demo app of usage with CleverMaps API
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
from cm_sdk import session, wrappers


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

    properties = ['poi_dwh.name', 'poi_dwh.lat', 'poi_dwh.lng', 'poi_dwh.type_name', 'poi_dwh.subtype_name', 'poi_dwh.weight']
    filter_by = [
        {
            "property": "poi_dwh.subtype_name",
            "operator": "in",
            "value": st.session_state.poi_subtype_selected
        }
    ]

    query_json = {
        "properties": properties,
        "filter_by": filter_by
    }

    rows_results = wrappers.query(st.session_state.cm_session, query_json, 20000)
    data = query_result_to_pd_data(rows_results)

    df = pd.DataFrame(data=data)
    df = df.rename(columns={'poi_dwh_name': 'name',
                            'poi_dwh_lng': 'lng',
                            'poi_dwh_lat': 'lat',
                            'poi_dwh_type_name': 'type_name',
                            'poi_dwh_subtype_name': 'subtype_name',
                            'poi_dwh_weight': 'weight'})

    df["radius"] = df["weight"].apply(lambda weight: weight+10)
    color_lookup = pdk.data_utils.assign_random_colors(df['subtype_name'])
    df['color'] = df.apply(lambda row: color_lookup.get(row['subtype_name']), axis=1)

    st.session_state.map_placeholder = st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=50.0698,
            longitude=14.4037,
            zoom=13,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position=['lng', 'lat'],
                #get_color='[200, 30, 0, 160]',
                get_color="color",
                get_radius="radius",
                radius_min_pixels=1,
                radius_max_pixels=100,
                pickable=True
            )
        ],
        tooltip={"text": "POI type: {type_name} \n POI subtype: {subtype_name} \n Name: {name} \n "}
        # tooltip={
        #     "html": "<b>adresse:</b> {address}"
        #             "<br/> <b>mape:</b> {pourc_err}"
        #             " <br/> <b>count:</b> {flow_value_count} "
        #             "<br/> <b>prediction:</b> {flow_value_streaming}"
        #             "<br/> <b>pedestrian ids:</b> {elevationValue}",
        #     "style": {"color": "white"},
        # }
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

    st.set_page_config(layout="wide")

    st.title('CleverMaps Demo Data App')

    poi_subtypes = wrappers.get_property_values(cm_session, 'poi_dwh.subtype_name')

    #st.selectbox('Select POI subtype to display', poi_subtypes, index=10, key='poi_subtype_selected')
    st.multiselect('Select POI subtype to display',
                   poi_subtypes,
                   key='poi_subtype_selected',
                   default=["atm", 'bank']
                   )

    map_placeholder = st.empty()
    st.session_state.map_placeholder = map_placeholder

    draw_map()

    #components.iframe('https://secure.clevermaps.io/#/v40dvff322hpko0e/map/review_view', width=1280, height=720)

    #st.write(st.session_state)



main()
