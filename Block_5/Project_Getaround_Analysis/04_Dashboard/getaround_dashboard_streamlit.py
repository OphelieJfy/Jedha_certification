"""

This script has the function of setting up a Streamlit
website serving as user interface for delay analysis
visualization and simumation as well as for daily rental
price prediction.

"""


############################################################
### Import useful librairies
############################################################

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import math
import requests
from PIL import Image
import json

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import streamlit as st
from streamlit_option_menu import option_menu


############################################################
### Functions definition and other parameters
############################################################

# Function to define rental checkout status
def get_checkout_state(row):

    state = "Unknown"

    if row["state"] == "ended":
        if row["delay_at_checkout_in_minutes"] <= 0:
            state = "On time checkout"
        elif row["delay_at_checkout_in_minutes"] >= 0:
            state = "Late checkout"

    elif row["state"] == "canceled":
        state = "Canceled"

    return state

# Function to define outliers
def detect_outliers(dataframe, feature_name):

    q1 = dataframe[feature_name].quantile(0.25)
    q3 = dataframe[feature_name].quantile(0.75)
    interquartile_range = q3 - q1
    upper_fence = math.ceil(q3 + 1.5 * interquartile_range)
    output = {
        'upper_fence': upper_fence,
    }

    return output

# Function to add vertical spaces
def spaces(iter):
    for i in range(iter):
        st.text("")


############################################################
### Main code with streamlit app definition
############################################################

if __name__ == '__main__':

    ###-----------------------------------------------------
    ### Define streamlit appearance
    ###-----------------------------------------------------

    with st.sidebar:

        choose = option_menu("Menu", ["Project presentation", "Late checkout analysis", "Fair price"],
                             icons = ["house", "watch", "key"],
                             menu_icon = "cast", default_index = 0,
                             styles = {
                                 "container": {"padding": "0!important", "background-color": "#EBDEF0"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "--hover-color": "#512E5F"},
                                 "nav-link-selected": {"background-color": "#AF7AC5"}
                             })


    ###-----------------------------------------------------
    ### Project presentation page
    ###-----------------------------------------------------

    if choose == "Project presentation":

        img = Image.open("Getaround.png")
        st.image(img)

        st.markdown(""" <style> .font {font-size:35px ; font-family: 'Cooper Black'; color: #633974;} </style> """, 
                    unsafe_allow_html = True)
        
        st.markdown("<p class='font'>Project overview</p>", 
                    unsafe_allow_html = True)
        
        st.markdown("""  
                    GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! 
                    Founded in 2009, this company has known rapid growth. 
                    In 2019, they count over 5 million users and about 20K available cars worldwide.  
                    """)
        
        st.subheader(':grey[Context]', divider = "grey")
        
        st.markdown("""
                    When renting a car, users have to complete a checkin flow at the beginning of the rental and a checkout flow at the end of the rental in order to:
                    - Assess the state of the car and notify other parties of pre-existing damages or damages that occured during the rental.
                    - Compare fuel level.
                    - Measure how many kilometers were driven.
                      
                    The checkin and checkout of rentals can be done with three distinct flows:
                    - **Mobile** rental agreement on native apps: driver and owner meet and both signe the rental agreement on the owner's smartphone
                    - **Connect** the driver doesn't meet the owner and opens the car with his smartphone
                    - **Paper** contract (negligible)  
                    """)
        
        st.subheader(':grey[Project]', divider = "grey")

        st.markdown("""
                    When using GetAround, drivers book cars for a specific time period, from an hour to a few days long. 
                    They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.  
                      
                    Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the 
                    same day: Customer service often reports users unsatisfied because they had to wait for the car to come back from the 
                    previous rental or users that even had to cancel their rental because the car wasn't returned on time.  
                      
                    In order to mitigate those issues GetAround has decided to implement a minimum delay between two rentals.
                    A car won't be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.  
                    Late checkout analysis and simulations can be found in the 'Late checkout analysis' section.  
                      
                    In addition to the above question, the Data Science team is working on pricing optimization. 
                    They have gathered some data to suggest optimum prices for car owners.  
                    Car rental prices estimator can be found in the 'Fair price' section.
                    """)
    
    ###-----------------------------------------------------
    ### Late checkout analysis page
    ###-----------------------------------------------------
    
    if choose == "Late checkout analysis":

        ###------------
        ### Page header
        ###------------

        # Page title
        st.title("🚘 Getaround : Late checkout analysis ⌚")

        # Page description
        st.markdown("""
                    Sometimes, users who rented a car on GetAround are late for their checkout.  
                    This can impact the next rental of the same vehicule, and thus the quality of service and customer satisfaction.  
                      
                    In order to mitigate those issues, GetAround has decided to implement a minimum delay between two rentals: 
                    a car won't be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.  
                      
                    As this minimum delay would impact GetAround and owners' revenues, the goal ofthis analysis is to provide some insights 
                    that helps product manager to decide:
                    - **the threshold**: how long should the minimum delay be?
                    - **the scope**: should they enable the feature for all cars or only Connect cars?
                    """)

        # Tabs
        tab_analysis, tab_simulation = st.tabs(["Analysis", "Simulation"])
        
        ###----------------------
        ### Load and prepare data
        ###----------------------

        # Load raw data
        data_path = "data/get_around_delay_analysis.xlsx"
        sheet_name = "rentals_data"
        @st.cache_data
        def load_data(nrows):
            df = pd.read_excel(data_path, sheet_name = sheet_name, nrows = nrows)
            return df
        raw_data = load_data(None)
        data = raw_data.copy()

        # Create column with precise state
        data["precise_state"] = data.apply(get_checkout_state, axis = 1)
        
        # Create column with checkout delay in minutes (>0)
        data["delays"] = data["delay_at_checkout_in_minutes"].apply(lambda x: 0 if x < 0 else x)
        
        # Define q3 / upper fence of checkout delay data
        late_checkouts_upper_fence = detect_outliers(data[data["precise_state"] == "Late checkout"], 'delay_at_checkout_in_minutes')['upper_fence']
        
        # Create new table with ckeckout delay impact
        data_copy = data.copy()
        data_merged = data.merge(data_copy, how = "left", left_on = "previous_ended_rental_id", right_on = "rental_id", suffixes = ["_current", "_previous"])
        data_with_previous = data_merged.dropna(subset = ["previous_ended_rental_id_current"])
        data_with_previous.loc[:, "checkin_delay"] = data_with_previous["delays_previous"] - data_with_previous["time_delta_with_previous_rental_in_minutes_current"]
        mask1 = (data_with_previous["state_current"] == "canceled")
        mask2 = (data_with_previous["checkin_delay"] > 0) & (data_with_previous["state_current"] == "ended")
        mask3 = (data_with_previous["checkin_delay"] < 0) & (data_with_previous["state_current"] == "ended")
        data_with_previous.loc[:, "checkout_delay_impact"] = np.select([mask1, mask2, mask3], 
                                                                    ["Cancelation", "Late checkin", "No impact"], 
                                                                    default = "No previous rental filled out")
        data_with_previous = data_with_previous[data_with_previous["precise_state_previous"] == "Late checkout"]
        
        # Create column with checkin delay in minutes (>0)
        data_with_previous["checkin"] = data_with_previous["checkin_delay"].apply(lambda x: 0 if x < 0 else x)

        # Define q3 / upper fence of ckechin delay data
        late_checkins_canceled_upper_fence = detect_outliers(data_with_previous[(data_with_previous["checkin"] > 0) & (data_with_previous["state_current"] == "canceled")], 'checkin')['upper_fence']

        ###-----------------------------------------------------
        ### Analysis tab
        ###-----------------------------------------------------

        with tab_analysis:

            ### Choose to see raw data or not
            show = st.radio("See data?", ["Hide data", "Show raw data"])
            
            if show == "Show raw data":
                st.write(raw_data)
                st.write(f"This dataset contains {len(raw_data)} rows.")
            st.markdown("""_Note: all analysis below are made on processed data_""")

            ### Main metrics
            st.subheader(':grey[Main metrics of the dataset]', divider = "grey")
            metrics_cols = st.columns([30, 30, 40])

            with metrics_cols[0]:
                st.metric(label = "Number of rentals :", value = len(data))
                st.metric(label = "Number of cars :", value = data["car_id"].nunique())

            with metrics_cols[1]:
                st.metric(label = "Proportion of 'Connect' rentals :", value = f"{round(len(data[data['checkin_type'] == 'connect']) / len(data) * 100, 2)} %")
                st.metric(label = "Proportion of 'Mobile' rentals :", value = f"{round(len(data[data['checkin_type'] == 'mobile']) / len(data) * 100, 2)} %")
            
            with metrics_cols[2]:
                st.metric(label = "Share of consecutive rentals of the same car :", value = f"{round(len(data[~data['previous_ended_rental_id'].isna()]) / len(data) * 100, 2)} %")
            
            ### Checkout overview
            st.subheader(':grey[Checkout overview]', divider = "grey")
            
            flow = st.selectbox("For which flow of checkout do you want to see data?", ["all", "connect", "mobile"])
            if flow == "all":
                flow_data = data
            else:
                flow_data = data[data["checkin_type"] == flow]

            checkout_cols = st.columns([60, 40])
            
            with checkout_cols[0]:

                checkout_pie = px.pie(flow_data, names = "precise_state", color = "precise_state",
                        color_discrete_map = {
                            "On time checkout": "limegreen",
                            "Late checkout": "gold",
                            "Canceled": "tomato",
                            "Unknown": "silver"},
                        category_orders = {"precise_state": ["On time checkout", "Late checkout", "Unknown", "Canceled"]},
                        title = f"<b> Rental checkout state ({flow}) <b>")
                st.plotly_chart(checkout_pie, use_container_width = True)
            
            with checkout_cols[1]:
                
                spaces(8)
                st.metric(
                    label = "Late checkouts with a delay of \n>less than 30 minutes :",
                    value = f"{round(len(flow_data[(flow_data['delays'] > 0) & (flow_data['delays'] <= 30)]) / len(flow_data) * 100, 2)}%"
                )
                st.metric(
                    label = "Late checkout with a delay of \n>more than 60 minutes :",
                    value = f"{round(len(flow_data[(flow_data['delays'] > 0) & (flow_data['delays'] > 60)]) / len(flow_data) * 100, 2)}%"
                )

            checkout_cols2 = st.columns([50, 50])
            
            with checkout_cols2[0]:
                
                state_histo = go.Figure()
                state_histo.add_trace(go.Histogram(
                    x = flow_data[flow_data["delays"] < late_checkouts_upper_fence]["delays"], 
                    marker_color = "royalblue"
                    ))
                state_histo.add_vline(x = flow_data['delays'].mean(), line_color = "midnightblue", line_dash = "dash", annotation_text = f"Mean delay = {flow_data['delays'].mean()}")
                state_histo.update_layout(title_text = f"<b> Distribution of rental checkout delays <br>({flow} - truncated outliers) <b>",
                                          xaxis_title_text = "Delay in minutes",
                                          yaxis_title_text = "Number of rentals"
                                          )
                st.plotly_chart(state_histo, use_container_width = True)

            with checkout_cols2[1]:
                
                state_box = px.box(
                    flow_data[flow_data["precise_state"] == "Late checkout"],
                    y = "delays",
                    labels = {"delays": "Delay in minutes"}, 
                    range_y = [0, late_checkouts_upper_fence+1]
                    )
                state_box.update_traces(marker_color = "gold")
                st.plotly_chart(state_box, use_container_width = True)

            ### Checkin overview
            st.subheader(':grey[Late checkout impact on next checkin (when existing)]', divider = "grey")
            
            flow_checkin = st.selectbox("For which flow of checkin do you want to see data?", ["all", "connect", "mobile"])
            if flow_checkin == "all":
                flow_checkin_data = data_with_previous
            else:
                flow_checkin_data = data_with_previous[data_with_previous["checkin_type_current"] == flow_checkin]

            checkin_cols = st.columns([60, 40])
            
            with checkin_cols[0]:
                
                checkin_pie = px.pie(flow_checkin_data[flow_checkin_data["checkout_delay_impact"] != "No previous rental filled out"], 
                    names = "checkout_delay_impact",
                    color = "checkout_delay_impact",
                    color_discrete_map = {
                        "No impact": "limegreen",
                        "Late checkin": "gold",
                        "Cancelation": "tomato"},
                    category_orders = {"checkout_delay_impact": ["No impact", "Late ckeckin", "Cancelation"]},
                    title = f"<b> Impact of checkout delays on checkin state ({flow_checkin}) <b>"
                    )
                st.plotly_chart(checkin_pie, use_container_width = True)
            
            with checkin_cols[1]:
                
                spaces(8)
                st.metric(
                    label = "Late checkin because of a \n>previous checkout delay :",
                    value = f"{round(len(flow_checkin_data[flow_checkin_data['checkin_delay'] > 0]) / len(flow_checkin_data) * 100, 2)}%"
                )
                st.metric(
                    label = "Late checkins canceled :",
                    value = f"{round(len(flow_checkin_data[(flow_checkin_data['checkin_delay'] > 0) & (flow_checkin_data['precise_state_current'] == 'Canceled')]) / len(flow_checkin_data[flow_checkin_data['checkin_delay'] > 0]) * 100, 2)}%"
                )
            
            checkin_cols2 = st.columns([50, 50])

            with checkin_cols2[0]:

                state_histo = go.Figure()
                state_histo.add_trace(go.Histogram(
                    x = flow_checkin_data[(flow_checkin_data["checkin"] > 0) & (flow_checkin_data["state_current"] == "canceled")]["checkin"], 
                    marker_color = "gold"
                    ))
                state_histo.add_vline(x = flow_checkin_data[(flow_checkin_data["checkin"] > 0) & (flow_checkin_data["state_current"] == "canceled")]["checkin"].mean(), 
                    line_color = "orange", line_dash = "dash", 
                    annotation_text = f"Mean checkin delay = <br>{flow_checkin_data[(flow_checkin_data['checkin'] > 0) & (flow_checkin_data['state_current'] == 'canceled')]['checkin'].mean()}"
                    )
                state_histo.update_layout(title_text = f"<b> Distribution of rental checkin delays <br>({flow_checkin} - truncated outliers) <b>",
                    xaxis_title_text = "Checkin delay in minutes",
                    yaxis_title_text = "Number of rentals"
                    )
                st.plotly_chart(state_histo, use_container_width = True)

            with checkin_cols2[1]:

                state_box = px.box(
                    flow_checkin_data[flow_checkin_data["checkin"] > 0],
                    y = "checkin",
                    labels = {"checkin": "Checkin delay in minutes"}, 
                    range_y = [0, late_checkins_canceled_upper_fence+1]
                    )
                state_box.update_traces(marker_color = "gold")
                st.plotly_chart(state_box, use_container_width = True)
        
        ###-----------------------------------------------------
        ### Simuation tab
        ###-----------------------------------------------------

        with tab_simulation:

            # Input form
            st.markdown("""Try to apply a minimum delay between consecutive rentals:""")
            with st.form(key = "simu"):
                simu_cols = st.columns([50, 50])
                with simu_cols[0]:
                    simu_scope = st.radio('Scope', ["All", "Connect"])
                with simu_cols[1]:
                    simu_threshold = st.number_input(label = "Threshold", min_value = 15, step = 15)
                submit = st.form_submit_button(label = "Apply")

            if submit:
                
                if simu_scope == "All":
                    df_simu = data_with_previous[data_with_previous["time_delta_with_previous_rental_in_minutes_current"] > simu_threshold]
                elif simu_scope == "Connect":
                    to_drop = data_with_previous[(data_with_previous["checkin_type_current"] == "connect") & (data_with_previous["time_delta_with_previous_rental_in_minutes_current"] < simu_threshold)]
                    df_simu = data_with_previous.drop(to_drop.index)
                
                st.markdown("""Impact of the minimal delay between consecutive rentals on checkins repartition after late checkout :""")

                if len(df_simu["checkout_delay_impact"]) == 0:
                    st.markdown("""_No more consecutive rentals_""")
                
                else:

                    checkout_impact_evolution_cols = st.columns([45, 10, 45])

                    with checkout_impact_evolution_cols[0]:
                        without_threshold_pie = checkin_pie
                        without_threshold_pie.update_layout(title = "<b> Without threshold </b>")
                        st.plotly_chart(without_threshold_pie, use_container_width = True)

                    with checkout_impact_evolution_cols[1]:
                        spaces(12)
                        arrow = Image.open("arrow.png")
                        st.image(arrow)

                    with checkout_impact_evolution_cols[2]:
                        with_threshold_pie = px.pie(df_simu[df_simu["checkout_delay_impact"] != "No previous rental filled out"], 
                            names = "checkout_delay_impact",
                            color = "checkout_delay_impact",
                            color_discrete_map = {
                                "No impact": "limegreen",
                                "Late checkin": "gold",
                                "Cancelation": "tomato"},
                            category_orders = {"checkout_delay_impact": ["No impact", "Late ckeckin", "Cancelation"]},
                            title = f"<b> With threshold </b>"
                            )
                        st.plotly_chart(with_threshold_pie, use_container_width = True)
                    
                    nb_canceled = len(data_with_previous[(data_with_previous['checkin_delay'] > 0) & (data_with_previous['precise_state_current'] == 'Canceled')])
                    nb_canceled_avoided = nb_canceled - len(df_simu[(df_simu['checkin'] > 0) & (df_simu['precise_state_current'] == 'Canceled')])
                    st.metric(
                        label = "Proportion of consecutive rentals loss :",
                        value = f"{round((len(data_with_previous) - len(df_simu)) / len(data_with_previous) * 100, 2)}%",
                    )
                    st.metric(
                        label = "Late-checkins-related cancelations avoided :",
                        value = f"{round(nb_canceled_avoided / nb_canceled * 100, 2)}%"
                    )
    

    ###-----------------------------------------------------
    ### Fair price page
    ###-----------------------------------------------------

    if choose == "Fair price":
        
        ###------------
        ### Page header
        ###------------

        # Page title
        st.title("🚘 Getaround : Fair price - daily rental price estimator 💰")

        # Page description
        st.markdown("""
                    When your are looking to rent your vehicule, it is sometimes difficult to find the right price. 
                    Indeed, it depends on many parameters.  
                      
                    This is why GetAround provides this simulator in order to best estimate the daily rental price of a vehicule, based on its characteristics.
                    """)
        spaces(3)

        st.markdown("""
                    Please complete this form to obtain your daily rental price estimation:  
                    """)
        spaces(1)

        # Provide all informations about the vehicule
        model_key = st.selectbox(
            'What brand is your vehicule?',
            ("Citroën", "Peugeot", "PGO", "Renault", "Audi", "BMW", "Mercedes", "Opel", "Volkswagen", "Ferrari", "Mitsubishi", "Nissan", "SEAT", "Subaru", "Toyota", "other"))
        mileage = st.text_input(
            "What is the mileage of your vehicule (enter an integer?",
            "")
        engine_power = st.text_input(
            "What is the engine power of your vehicule (enter an integer)?",
            "")
        fuel = st.selectbox(
            "What is the fuel of your vehicule?",
            ("diesel", "petrol", "other"))
        paint_color = st.selectbox(
            "What is the color of your vehicule?",
            ("black", "grey", "white", "red", "silver", "blue", "beige", "brown", "other"))
        car_type = st.selectbox(
            "What is the type of your vehicule?",
            ("convertible", "coupe", "estate", "hatchback", "sedan", "subcompact", "suv", "van"))
        private_parking_available = st.selectbox(
            "Do you have a private parking available for your vehicule?",
            ("True", "False"))
        has_gps = st.selectbox(
            "Is your vehicule equipped with GPS?",
            ("True", "False"))
        has_air_conditioning = st.selectbox(
            "Is your vehicule equipped with air conditioning?",
            ("True", "False"))
        automatic_car = st.selectbox(
            "Does your vehicule have an automatic transmission?",
            ("True", "False"))
        has_getaround_connect = st.selectbox(
            "Is your vehicule equipped with GetAround connect?",
            ("True", "False"))
        has_speed_regulator = st.selectbox(
            "Does your vehicule have speed regulator?",
            ("True", "False"))
        winter_tires = st.selectbox(
            "Is your vehicule equipped with winter tires?",
            ("True", "False"))
            
        # Prepare data and request API
        api_url = "https://ojo-getaround-api-fa638883c2ea.herokuapp.com/predict"
        data = [{
            "model_key": model_key,
            "mileage": mileage,
            "engine_power": engine_power,
            "fuel": fuel,
            "paint_color": paint_color,
            "car_type": car_type,
            "private_parking_available": private_parking_available,
            "has_gps": has_gps,
            "has_air_conditioning": has_air_conditioning,
            "automatic_car": automatic_car,
            "has_getaround_connect": has_getaround_connect,
            "has_speed_regulator": has_speed_regulator,
            "winter_tires": winter_tires
        }]

        if st.button("Estimate my daily price"):

            st.markdown(""" <style> .font {font-size:16px ; font-family: 'Cooper Black'; color: #633974;} </style> """, 
                    unsafe_allow_html = True)

            try: 

                response = requests.post(api_url, data = json.dumps(data), headers={'Content-Type': 'application/json'})
                price = response.json()['prediction'][0]
                spaces(1)
                st.markdown(f"<p class='font'><u>Estimation:</u> <br/>You can propose your vehicule for rental at an average price of <b>{round(price,2)} euros</b> per day.</p>", 
                    unsafe_allow_html = True)

            except:

                spaces(1)
                st.markdown(f"<p class='font'>Please complete all the requested fields.</p>", 
                    unsafe_allow_html = True)

            