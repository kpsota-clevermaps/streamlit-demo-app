"""
# Streamlit + CleverMaps API demo app
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
from clevermaps_sdk import sdk


def query_result_to_pd_data(metric_results):

    data = {}
    for mr in metric_results:
        for prop in list(mr['content'].keys()):
            if prop not in data:
                data[prop] = []
            data[prop].append(mr['content'][prop])

    return data

def get_data():

    pass


def render_table():

    pass

def render_plot():

    pass

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

    rows_results = st.session_state.cm_sdk.query(query_json, 20000)
    #data = query_result_to_pd_data(rows_results)

    df = pd.DataFrame(data=rows_results)
    df = df.rename(columns={'poi_dwh_name': 'name',
                            'poi_dwh_lng': 'lng',
                            'poi_dwh_lat': 'lat',
                            'poi_dwh_type_name': 'type_name',
                            'poi_dwh_subtype_name': 'subtype_name',
                            'poi_dwh_weight': 'weight'})

    df["radius"] = df["weight"].apply(lambda weight: weight+10)
    color_lookup = pdk.data_utils.assign_random_colors(df['subtype_name'])
    df['color'] = df.apply(lambda row: color_lookup.get(row['subtype_name']), axis=1)

    st.session_state.data = df

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

    cm_sdk = sdk.Sdk(access_token, project_id)
    st.session_state.cm_sdk = cm_sdk

    st.set_page_config(layout="wide")

    st.title('CleverMaps Demo Data App')

    poi_subtypes = cm_sdk.get_property_values('poi_dwh.subtype_name')

    #st.selectbox('Select POI subtype to display', poi_subtypes, index=10, key='poi_subtype_selected')
    st.multiselect('Select POI subtype to display',
                   poi_subtypes,
                   key='poi_subtype_selected',
                   default=["atm", 'bank']
                   )

    map_placeholder = st.empty()
    st.session_state.map_placeholder = map_placeholder

    chart_placeholder = st.empty()
    st.session_state.chart_placeholder = chart_placeholder

    table_placeholder = st.empty()
    st.session_state.table_placeholder = table_placeholder

    draw_map()

    query_json = {
        'properties': ['poi_dwh.subtype_name'],
        'metrics': ["pois_count_metric"],
        'filter_by': [
            {
                "property": "poi_dwh.subtype_name",
                "operator": "in",
                "value": st.session_state.poi_subtype_selected
            }
        ]
    }
    poi_subtypes_counts = cm_sdk.query(query_json)
    poi_subtypes_counts_df = poi_subtypes_counts
    #poi_subtypes_counts_df = query_result_to_pd_data(poi_subtypes_counts)

    vega_chart_config = {
      "width": 300,
      "encoding": {
            "y": {
                "field": "poi_dwh_subtype_name",
                "type": "nominal",
                "title": None,
                "axis": {
                    "domain": False,
                    "grid": False,
                    "ticks": False
                }
            },
            "x": {
                "field": "pois_count_metric",
                "type": "quantitative",
                "title": None,
                "axis": {
                    "domain": False,
                    "grid": False,
                    "ticks": False,
                    "labels": False
                }
            }
          },
        "layer": [{
            "mark": "bar"
        }, {
            "mark": {
                "type": "text",
                "align": "left",
                "baseline": "middle",
                "dx": 3
            },
            "encoding": {
                "text": {"field": "pois_count_metric", "type": "quantitative"}
            }
        }]
    }


    #st.session_state.chart_placeholder = st.vega_lite_chart(poi_subtypes_counts_df, vega_chart_config)

    st.session_state.table_placeholder = st.dataframe(poi_subtypes_counts_df)

    #st.write(st.session_state)



main()
