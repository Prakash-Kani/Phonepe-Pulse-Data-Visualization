import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import mysql.connector
import main_def
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MYSQL Connection
mysql_host_name = os.getenv("MYSQL_HOST_NAME")
mysql_user_name = os.getenv("MYSQL_USER_NAME")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database_name = os.getenv("MYSQL_DATABASE_NAME")

db = mysql.connector.connect(host = mysql_host_name,
                             user = mysql_user_name,
                             password = mysql_password,
                             database = mysql_database_name)
mycursor = db.cursor(buffered = True)

# db = mysql.connector.connect(host = 'localhost',
#                              user = 'root',
#                              password = 'Prakashk14',
#                              database = 'phonepe')
# mycursor = db.cursor(buffered = True)

def Number_Conversion(number):
    if number // 10**7:
        number = f'{round(number / 10**7,2)} Crores'
    elif number // 10**5:
        number = f'{round(number / 10**5,2)} Lakhs'
    elif number // 10**3:
        number = f'{round(number / 10**3,2)} K'
    return number


url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
response = requests.get(url)
data1 = json.loads(response.content)
geo_state=[i['properties'].get('ST_NM') for i in data1['features']]
geo_state1=geo_state.sort(reverse=False)



st.set_page_config(
    page_title="PhonePe Pulse",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------/  Theme Setting /--------------------------------------------------------------
# [theme]
primaryColor="#289dbf"
backgroundColor="#2F0350"
secondaryBackgroundColor="#4f067d"
textColor="#ffffff"


st.sidebar.header(":violet[**PhonePe Pulse**]")
with st.sidebar:
    selected = option_menu("Menu", ["Explore Data","Analysis","Home"], 
                # icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                menu_icon= "menu-button-wide",
                default_index=0,
                )
    tran_type = st.sidebar.selectbox('**Select the Type of Transcation**',['Recharge & bill payments', 'Peer-to-peer payments','Merchant payments', 'Financial Services','Others'])
    year=st.sidebar.selectbox('**Select Year**',[2018, 2019, 2020, 2021, 2022, 2023])

    if year == 2023:
        quarter = st.sidebar.selectbox('**Select Quarter**',[1,2])
    else:
        quarter = st.sidebar.selectbox('**Select Quarter**',[1,2,3,4])
if selected == "Explore Data":
    st.markdown("# :violet[PhonePe Pulse Data Visualization and Exploration]")
    # st.markdown("## :violet[A User-Friendly Tool Using Streamlit and Plotly]")
    tab1, tab2= st.tabs(['**Transaction**','**User**'])
    with tab1:
        # if tab1:
        #     tran_type = st.sidebar.selectbox('**Select the Type of Transcation**',['Recharge & bill payments', 'Peer-to-peer payments','Merchant payments', 'Financial Services','Others'])

        col1, col2 = st.columns([2,1], gap='medium')
        with col2:
            st.header(':blue[**Transaction**]', divider = 'rainbow')
            
            mycursor.execute(f"""SELECT g.Transaction_Type, g.Total_Amount, g.Total_Count,  round((g.Total_Amount / g.Total_Count),2) as Average_Transaction
                                FROM (SELECT Transaction_Type, sum(Transaction_Amount)as Total_Amount, sum(Transaction_Count) as Total_Count FROM aggregated_transaction 
                                WHERE Year = {year} AND Quarter = {quarter} GROUP BY Transaction_Type) as g;""")
            data = mycursor.fetchall()
            df1=pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
            st.markdown('### ***All PhonePe transactions (UPI + Cards + Wallets***)')
            totalcount=df1['Total_Count'].sum()
            st.markdown(f'## :blue[{totalcount}]')
            # st.write(totalcount)
            st.markdown('#### ***Total payment value***')
            totalamount=df1['Total_Amount'].sum()
            st.markdown(f'#### :blue[{Number_Conversion(totalamount)}]')
            # st.write(totalamount)
            st.markdown('#### ***Avg. transaction value***')
            # average=totalamount//totalcount
            average= df1['Average_Transaction'].mean()
            st.markdown(f'### :blue[{round(average)}]')
            # st.write(average) 
            st.header(':blue[Categories]', divider='rainbow')
            for i in range(df1.shape[0]):
                st.markdown(f"""###### {i + 1}.  {df1['Transaction_Type'].iloc[i]} <=> :blue[{Number_Conversion(df1['Total_Amount'].iloc[i])}]""")
            bar1=st.button('Bar Graph')
            col3,col4,col5 =st.columns([1,1,2])
            with col3:
                Tran_state_button = st.button('State')
            with col4:
                Tran_district_button = st.button('District')
            with col5:
                Tran_pincode_button = st.button('Postal Code')
            if Tran_state_button:
                # mycursor.execute(f"""SELECT top.State, top.Total_Transaction_Count
                #                 FROM (
                #                     SELECT State, SUM(Transaction_Count) as Total_Transaction_Count
                #                     FROM top_transaction_district
                #                     WHERE Year = {year} AND Quarter = {quarter}
                #                     GROUP BY State
                #                 ) as top
                #                 ORDER BY top.Total_Transaction_Count desc limit 10;""")
                # data1 = mycursor.fetchall()
                # df2=pd.DataFrame(data1, columns = [i[0] for i in mycursor.description])
                # for i in range(df2.shape[0]):
                #     st.markdown(f"""##### {i + 1}.  {df2['State'].iloc[i]} :blue[{Number_Conversion(df2['Total_Transaction_Count'].iloc[i])}]""")
                st.header(':blue[Top 10 State Transaction Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT State, Total_Transaction_Count FROM top_transaction_state
                                    WHERE Year = {year} AND Quarter = {quarter}
                                ORDER BY Total_Transaction_Count desc limit 10;""")
                data1 = mycursor.fetchall()
                df2=pd.DataFrame(data1, columns = [i[0] for i in mycursor.description])
                for i in range(df2.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df2['State'].iloc[i].title()} <=> :blue[{Number_Conversion(df2['Total_Transaction_Count'].iloc[i])}]""")

            elif Tran_district_button:
                st.header(':blue[Top 10 District Transaction Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT top.District, top.Total_Transaction_Count
                                FROM (
                                    SELECT District, SUM(Transaction_Count) as Total_Transaction_Count
                                    FROM top_transaction_district
                                    WHERE Year = {year} AND Quarter = {quarter}
                                    GROUP BY District
                                ) as top
                                ORDER BY top.Total_Transaction_Count desc limit 10;""")
                data2 = mycursor.fetchall()
                df3=pd.DataFrame(data2, columns = [i[0] for i in mycursor.description])
                for i in range(df3.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df3['District'].iloc[i].title()} <=> :blue[{Number_Conversion(df3['Total_Transaction_Count'].iloc[i])}]""")
            elif Tran_pincode_button:
                st.header(':blue[Top 10 Postal Code Transaction Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT Pincode, Transaction_Count
                                    FROM top_transaction_pincode
                                    WHERE Year =2018 AND Quarter =1
                                    ORDER BY Transaction_Count DESC LIMIT 10;""")
                data3 = mycursor.fetchall()
                df4=pd.DataFrame(data3, columns = [i[0] for i in mycursor.description])
                for i in range(df4.shape[0]):
                    st.markdown(f"##### {i + 1}.  {df4['Pincode'].iloc[i]} <=> :blue[{Number_Conversion(df4['Transaction_Count'].iloc[i])}]")
            else:
                st.header(':blue[Top 10 State Transaction Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT State, Total_Transaction_Count FROM top_transaction_state
                                    WHERE Year = {year} AND Quarter = {quarter}
                                ORDER BY Total_Transaction_Count desc limit 10;""")
                data1 = mycursor.fetchall()
                df2=pd.DataFrame(data1, columns = [i[0] for i in mycursor.description])
                for i in range(df2.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df2['State'].iloc[i].title()} <=> :blue[{Number_Conversion(df2['Total_Transaction_Count'].iloc[i])}]""")

        with col1:
            if year and quarter:
                fig = main_def.transaction_geo_fig1(year, quarter)
                st.plotly_chart(fig)

            #------------------------------------------------------/aggregated transaction/-------------------
            if year and quarter and tran_type:
                fig1 = main_def.transaction_geo_fig2(year, quarter,tran_type)
                st.plotly_chart(fig1)

            if Tran_state_button:
                # st.write(df2 )
                bargraph1 = main_def.top10_transaction_state_fig(year, quarter)
                st.plotly_chart(bargraph1,use_container_width=True)


            elif Tran_district_button:
                bargraph2 = main_def.top10_transaction_district_fig(year, quarter)
                st.plotly_chart(bargraph2,use_container_width=True)

            elif Tran_pincode_button:
                bargraph3 = main_def.top10_transaction_pincode_fig(year, quarter)
                st.plotly_chart(bargraph3,use_container_width=True)


            elif bar1:
                new=px.bar(df1, x = 'Total_Amount', y ='Transaction_Type', text = 'Total_Amount', color='Total_Amount',
                            color_continuous_scale = 'thermal', title = 'Transaction Category Analysis Chart', height = 600, orientation= 'h')
                new.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(new,use_container_width=True)
            
            else:
                # st.write(df2 )
                bargraph1 = main_def.top10_transaction_state_fig(year, quarter)
                st.plotly_chart(bargraph1,use_container_width=True)

    with tab2:
        col6,col7 =st.columns([2, 1], gap = 'medium')
        with col7:
            st.header(':blue[**USERS**]', divider = 'rainbow')
            
            mycursor.execute(f"""SELECT State, sum(Registered_User) as Registered_PhonePe_Users, sum(App_Opens) as PhonePe_App_Opens FROM map_user 
                                 WHERE Year = {year} AND Quarter = {quarter} GROUP BY State ORDER BY State;""")
            data1 = mycursor.fetchall()
            df5=pd.DataFrame(data1, columns = [i[0] for i in mycursor.description])
            st.markdown(f'##### :blue[***Registered PhonePe users till {quarter} {year}***]')
            registeredcount=df5['Registered_PhonePe_Users'].sum()
            st.markdown(f'## {registeredcount}')
            st.markdown(f'##### :blue[***PhonePe app opens in {quarter} {year}***]')
            appopens=df5['PhonePe_App_Opens'].sum()
            st.markdown(f'#### {Number_Conversion(appopens)}')
            st.header(':blue[***Brand Analysis***]', divider = 'rainbow')
            mycursor.execute(f"""SELECT g.Brand, g.Total_User_Count, g.User_Precentage
                                FROM (SELECT Brand, sum(User_Count)as Total_User_Count, sum(Percentage) as User_Precentage FROM aggregated_user 
                                WHERE Year = {year} AND Quarter = {quarter} GROUP BY Brand) as g
                                ORDER BY Total_User_Count DESC LIMIT 10;""")
            data2 = mycursor.fetchall()
            brand=pd.DataFrame(data2, columns = [i[0] for i in mycursor.description])
            for i in range(brand.shape[0]):
                st.markdown(f"##### {i+1}. {brand['Brand'].iloc[i]} <=> :blue[{Number_Conversion(brand['Total_User_Count'].iloc[i])}]")
            # st.header('',divider ='gray')
            
            st.header('', divider='rainbow')
            col8,col9,col10 =st.columns([1,1,2])
            with col8:
                state_button = st.button('State ')
            with col9:
                district_button = st.button('District ')
            with col8:
                pincode_button = st.button('Postal Code ')
            if state_button:
                # mycursor.execute(f"""SELECT State, sum(Registered_User) as Registered_User FROM top_user_district 
                #                  WHERE Year = {year} AND Quarter = {quarter} GROUP BY State ORDER BY Registered_User DESC LIMIT 10;""")
                # data8 = mycursor.fetchall()
                # df6 = pd.DataFrame(data8, columns = [i[0] for i in mycursor.description])
                # for i in range(df6.shape[0]):
                #     st.markdown(f"""##### {i + 1}.  {df6['State'].iloc[i]} :blue[{Number_Conversion(df6['Registered_User'].iloc[i])}]""")
                st.header(':blue[Top 10 State User Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT State, Total_Registered_Users FROM top_user_state 
                                 WHERE Year = {year} AND Quarter = {quarter} ORDER BY Total_Registered_Users DESC LIMIT 10;""")
                data8 = mycursor.fetchall()
                df6 = pd.DataFrame(data8, columns = [i[0] for i in mycursor.description])
                for i in range(df6.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df6['State'].iloc[i].title()} <=> :blue[{Number_Conversion(df6['Total_Registered_Users'].iloc[i])}]""")
                
            elif district_button:
                st.header(':blue[Top 10 District User Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT District, sum(Registered_User) as Registered_User FROM top_user_district 
                                 WHERE Year = {year} AND Quarter = {quarter} GROUP BY District ORDER BY Registered_User DESC LIMIT 10;""")
                data9 = mycursor.fetchall()

                df7 = pd.DataFrame(data9, columns = [i[0] for i in mycursor.description])
                for i in range(df7.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df7['District'].iloc[i].title()} <=> :blue[{Number_Conversion(df7['Registered_User'].iloc[i])}]""")
                
            elif pincode_button:
                st.header(':blue[Top 10 Postal Code User Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT Pincode, Registered_User FROM top_user_pincode 
                                 WHERE Year = {year} AND Quarter = {quarter} ORDER BY Registered_User DESC LIMIT 10;""")
                data10 = mycursor.fetchall()

                df8 = pd.DataFrame(data10, columns = [i[0] for i in mycursor.description])
                for i in range(df8.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df8['Pincode'].iloc[i]} <=> :blue[{Number_Conversion(df8['Registered_User'].iloc[i])}]""")
            else:
                st.header(':blue[Top 10 State User Analysis]', divider='rainbow')
                mycursor.execute(f"""SELECT State, Total_Registered_Users FROM top_user_state 
                                 WHERE Year = {year} AND Quarter = {quarter} ORDER BY Total_Registered_Users DESC LIMIT 10;""")
                data8 = mycursor.fetchall()
                df6 = pd.DataFrame(data8, columns = [i[0] for i in mycursor.description])
                for i in range(df6.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df6['State'].iloc[i].title()} <=> :blue[{Number_Conversion(df6['Total_Registered_Users'].iloc[i])}]""")

        with col6:
            if year and quarter:

            
                fig = main_def.user_geo_fig1(year, quarter)
                st.plotly_chart(fig)
#-----------------------------------------------/ Aggregated user figure/---------------------------------------------------------------------
            if year and quarter:
                fig1 = main_def.user_treemap_fig2(year, quarter)
                st.plotly_chart(fig1)

            if state_button:
                bargraph4 = main_def.top10_user_state_fig(year, quarter)
                st.plotly_chart(bargraph4,use_container_width=True)

            elif district_button:
                bargraph5 = main_def.top10_user_district_fig(year, quarter)
                st.plotly_chart(bargraph5,use_container_width=True)

            elif pincode_button:
                bargraph6 = main_def.top10_user_pincode_fig(year, quarter)
                st.plotly_chart(bargraph6,use_container_width=True)

            else:
                bargraph4 = main_def.top10_user_state_fig(year, quarter)
                st.plotly_chart(bargraph4,use_container_width=True)
elif selected == "Analysis":
    analysis_type = st.selectbox('**Select the Type of Analysis**',['Day','Month'])
    if year and quarter and tran_type:
        if analysis_type == 'Day':
            fig = main_def.Day_Analysis(year, quarter, tran_type)
            st.plotly_chart(fig)
            barchart = main_def.Day_Analysis_barchart(year, quarter, tran_type)
            st.plotly_chart(barchart, use_container_width=True)
        elif analysis_type == 'Month':
            fig = main_def.Month_Analysis(year, quarter, tran_type)
            st.plotly_chart(fig)
            barchart = main_def.Month_Analysis_barchart(year, quarter, tran_type)
            st.plotly_chart(barchart, use_container_width=True)
elif selected == "Home":
    st.header(":red[***Welcome To PhonePe Pulse Data Extraction***]")
    st.markdown("""#####  In this app, we explore and analyze data from PhonePe Pulse, a powerful data visualization and analytics provided by PhonePe, a leading digital payment service in India. PhonePe Pulse offers comprehensive  insights into digital payment trends, transaction data, user behaviors, and more. This project aims to provide a brief overview of the capabilities and features of PhonePe Pulse data visualization. """)
    st.markdown(""" ## :blue[**Introduction to PhonePe Pulse**]""")
    st.markdown(""" #####  :red[**PhonePe Pulse**]  is a feature-rich dashboard and data visualization tool that enables businesses and users to gain a deeper understanding of digital payment trends, transaction data, and consumer behaviors. With PhonePe Pulse, you can unlock valuable insights and make data-driven decisions. Here are some key aspects of PhonePe Pulse: """)
    st.markdown(""" -  :blue[**Transaction Insights:**] Explore various transaction types, including UPI payments, digital wallet transactions, 
                and more.Analyze transaction data for specific time periods, regions, and transaction categories.""")
    st.markdown(""" - :blue[**Geographical Analysis:**] Gain insights into transactions across different Indian states and regions. 
                    Understand transaction volume, values, and trends at a regional level.""")
    st.markdown(" - :blue[**User Behavior:**] Get a better understanding of user demographics, preferences, and engagement patterns.")
    st.markdown(" - :blue[**Trend Analysis:**] Track growth trends in different transaction types, identify seasonality, and more.")
    st.markdown(" - :blue[**User Engagement:**] Learn how and when users engage with the PhonePe app, helping businesses optimize their offerings.")
    st.markdown(""" - :blue[**Payment Categories:**] Explore transaction data related to various payment categories, such as mobile recharges, 
                bill payments, peer-to-peer transfers, and more.""")
    st.markdown(" - :blue[**Data Export:**] Easily export data for further analysis or reporting.")
    st.markdown(" - :blue[**Custom Dashboards:**] Create custom dashboards and visualizations to meet your specific needs and preferences.")
    st.markdown(" This project aims to showcase the capabilities of PhonePe Pulse and the insights it can offer to businesses and individual users.")
    st.markdown(" This project will be divided into several sections, each focusing on specific aspects of PhonePe Pulse data, analysis, and visualization. Stay tuned as we dive into the world of digital payment insights!")
