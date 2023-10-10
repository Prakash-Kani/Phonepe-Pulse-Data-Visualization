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
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()

# # MYSQL Connection
# mysql_host_name = os.getenv("MYSQL_HOST_NAME")
# mysql_user_name = os.getenv("MYSQL_USER_NAME")
# mysql_password = os.getenv("MYSQL_PASSWORD")
# mysql_database_name = os.getenv("MYSQL_DATABASE_NAME")

# db = mysql.connector.connect(host = mysql_host_name,
#                              user = mysql_user_name,
#                              password = mysql_password,
#                              database = mysql_database_name)
# mycursor = db.cursor(buffered = True)

db = mysql.connector.connect(host = 'localhost',
                             user = 'root',
                             password = 'Prakashk14',
                             database = 'phonepe')
mycursor = db.cursor(buffered = True)

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
    selected = option_menu("Menu", ["Explore Data","About"], 
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
    st.markdown("# :violet[Data Visualization and Exploration]")
    st.markdown("## :violet[A User-Friendly Tool Using Streamlit and Plotly]")
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
            st.markdown(f"""##### 1.  {df1['Transaction_Type'].iloc[0]} :blue[{Number_Conversion(df1['Total_Amount'].iloc[0])}]
                                \n2.  {df1['Transaction_Type'].iloc[1]} :blue[{Number_Conversion(df1['Total_Amount'].iloc[1])}]
                                \n3.  {df1['Transaction_Type'].iloc[2]} :blue[{Number_Conversion(df1['Total_Amount'].iloc[2])}]
                                \n4.  {df1['Transaction_Type'].iloc[3]} :blue[{Number_Conversion(df1['Total_Amount'].iloc[3])}]
                                \n5.  {df1['Transaction_Type'].iloc[4]} :blue[{Number_Conversion(df1['Total_Amount'].iloc[4])}]""")
            bar1=st.button('Bar Graph')
            st.header(':blue[Top 10 states]', divider='rainbow')
            # c=st.button('State')
            # d=st.button('district')
            col3,col4,col5 =st.columns([1,1,2])
            with col3:
                Tran_state_button = st.button('State')
            with col4:
                Tran_district_button = st.button('District')
            with col5:
                Tran_pincode_button = st.button('Postal Code')
            if Tran_state_button:
                mycursor.execute(f"""SELECT top.State, top.Total_Transaction_Amount
                                FROM (
                                    SELECT State, SUM(Transaction_Amount) as Total_Transaction_Amount
                                    FROM top_transaction_state
                                    WHERE Year = {year} AND Quarter = {quarter}
                                    GROUP BY State
                                ) as top
                                ORDER BY top.Total_Transaction_Amount desc limit 10;""")
                data1 = mycursor.fetchall()
                df2=pd.DataFrame(data1, columns = [i[0] for i in mycursor.description])
                for i in range(df2.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df2['State'].iloc[i]} :blue[{Number_Conversion(df2['Total_Transaction_Amount'].iloc[i])}]""")

            elif Tran_district_button:
                mycursor.execute(f"""SELECT top.District, top.Total_Transaction_Amount
                                FROM (
                                    SELECT District, SUM(Transaction_Amount) as Total_Transaction_Amount
                                    FROM top_transaction_state
                                    WHERE Year = {year} AND Quarter = {quarter}
                                    GROUP BY District
                                ) as top
                                ORDER BY top.Total_Transaction_Amount desc limit 10;""")
                data2 = mycursor.fetchall()
                df3=pd.DataFrame(data2, columns = [i[0] for i in mycursor.description])
                for i in range(df3.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df3['District'].iloc[i]} :blue[{Number_Conversion(df3['Total_Transaction_Amount'].iloc[i])}]""")
            elif Tran_pincode_button:
                mycursor.execute(f"""SELECT Pincode, Transaction_Amount
                                    FROM top_transaction_pincode
                                    WHERE Year =2018 AND Quarter =1
                                    ORDER BY Transaction_Amount DESC LIMIT 10;""")
                data3 = mycursor.fetchall()
                df4=pd.DataFrame(data3, columns = [i[0] for i in mycursor.description])
                for i in range(df4.shape[0]):
                    st.markdown(f"##### {i + 1}.  {df4['Pincode'].iloc[i]} :blue[{Number_Conversion(df4['Transaction_Amount'].iloc[i])}]")

        with col1:
            if year and quarter:

                mycursor.execute(f"""SELECT g.State, g.Total_Transaction_Count, g.Total_Transaction_Amount,
                                    round((g.Total_Transaction_Amount / g.Total_Transaction_Count),2) as Average_Transaction_Amount
                                FROM (
                                    SELECT State, 
                                        SUM(Transaction_Count) as Total_Transaction_Count, 
                                        SUM(Transaction_Amount) as Total_Transaction_Amount
                                    FROM map_transaction  
                                    WHERE Year = 2018 AND Quarter = 1 
                                    GROUP BY State
                                ) as g;""")
                data4 = mycursor.fetchall()
                # print(data4)

                dff = pd.DataFrame(data4, columns = [i[0] for i in mycursor.description])

            dff['State']=geo_state

            fig = px.choropleth(
                dff,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='Total_Transaction_Amount',
                hover_name='State',
                custom_data=['Total_Transaction_Count','Total_Transaction_Amount', 'Average_Transaction_Amount'],
                color_continuous_scale='purples')

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Transaction Count = %{customdata[0]}<br>Transaction Amount = %{customdata[1]}<br>Average Transaction Amount = %{customdata[2]}')

            st.plotly_chart(fig)

            #------------------------------------------------------/aggregated transaction/-------------------
            if year and quarter and tran_type:

                mycursor.execute(f"""select State, Transaction_Count, Transaction_Type, Transaction_Amount,(Transaction_Amount/Transaction_Count) as Avearge_Amount from aggregated_transaction 
                                where  year={year} and quarter={quarter} and Transaction_Type = '{tran_type}';""")
                data4 = mycursor.fetchall()
                # print(data4)

                dff = pd.DataFrame(data4, columns = [i[0] for i in mycursor.description])

            dff['State']=geo_state

            fig = px.choropleth(
                dff,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='Transaction_Amount',
                hover_name='State',
                custom_data=['Transaction_Type', 'Transaction_Count', 'Transaction_Amount', 'Avearge_Amount'],
                color_continuous_scale='rainbow')

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Transaction Type = %{customdata[0]}<br>Transaction Count = %{customdata[1]}<br>Transaction Amount = %{customdata[2]}<br>Avearge Amount = %{customdata[3]}')

            st.plotly_chart(fig)

            if Tran_state_button:
                # st.write(df2 )
                bargraph1 = px.bar(df2, x ='State', y = 'Total_Transaction_Amount', text = 'Total_Transaction_Amount', color='Total_Transaction_Amount',
                            color_continuous_scale = 'thermal', title = 'Top 10 State Transaction Analysis Chart', height = 600)
                bargraph1.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph1,use_container_width=True)


            if Tran_district_button:
                bargraph2 = px.bar(df3, x ='District', y = 'Total_Transaction_Amount', text = 'Total_Transaction_Amount', color='Total_Transaction_Amount',
                            color_continuous_scale = 'thermal', title = 'Top 10 District Transaction Analysis Chart', height = 600)
                bargraph2.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph2,use_container_width=True)

            if Tran_pincode_button:
                newdf=df4
                newdf['Pincode'] = newdf['Pincode'].astype(str)
                bargraph3 = px.bar(newdf, x ='Pincode', y = 'Transaction_Amount', text = 'Transaction_Amount', color='Transaction_Amount',
                            color_continuous_scale = 'thermal', title = 'Top 10 Postal Code Transaction Analysis Chart', height = 600)
                bargraph3.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph3,use_container_width=True)


            if bar1:
                new=px.bar(df1, x = 'Total_Amount', y ='Transaction_Type', text = 'Total_Amount', color='Total_Amount',
                            color_continuous_scale = 'thermal', title = 'Transaction Category Analysis Chart', height = 600, orientation= 'h')
                new.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(new,use_container_width=True)


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

            col8,col9,col10 =st.columns(3)
            with col8:
                state_button = st.button('State ')
            with col9:
                district_button = st.button('District ')
            with col8:
                pincode_button = st.button('Postal Code ')
            st.header('', divider='rainbow')
            mycursor.execute('select DISTINCT(State) from aggeregated_user;')
            data11=mycursor.fetchall()
            brand_state=st.selectbox('select the state',[i[0] for i in data11])
            st.write('click the "Brand Analysis" button')
            brand=st.button('Brand Analysis')
            if state_button:
                mycursor.execute(f"""SELECT State, sum(Registered_User) as Registered_User FROM top_user_district 
                                 WHERE Year = {year} AND Quarter = {quarter} GROUP BY State ORDER BY Registered_User DESC LIMIT 10;""")
                data8 = mycursor.fetchall()
                df6 = pd.DataFrame(data8, columns = [i[0] for i in mycursor.description])
                for i in range(df6.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df6['State'].iloc[i]} :blue[{Number_Conversion(df6['Registered_User'].iloc[i])}]""")
                
            elif district_button:
                mycursor.execute(f"""SELECT District, sum(Registered_User) as Registered_User FROM top_user_district 
                                 WHERE Year = {year} AND Quarter = {quarter} GROUP BY District ORDER BY Registered_User DESC LIMIT 10;""")
                data9 = mycursor.fetchall()

                df7 = pd.DataFrame(data9, columns = [i[0] for i in mycursor.description])
                for i in range(df7.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df7['District'].iloc[i]} :blue[{Number_Conversion(df7['Registered_User'].iloc[i])}]""")
                
            elif pincode_button:
                mycursor.execute(f"""SELECT Pincode, Registered_User FROM top_user_pincode 
                                 WHERE Year = {year} AND Quarter = {quarter} ORDER BY Registered_User DESC LIMIT 10;""")
                data10 = mycursor.fetchall()

                df8 = pd.DataFrame(data10, columns = [i[0] for i in mycursor.description])
                for i in range(df8.shape[0]):
                    st.markdown(f"""##### {i + 1}.  {df8['Pincode'].iloc[i]} :blue[{Number_Conversion(df8['Registered_User'].iloc[i])}]""")
                
        with col6:
            if year and quarter:

                mycursor.execute(f"""SELECT State, sum(Registered_User) as Registered_PhonePe_Users, sum(App_Opens) as PhonePe_App_Opens FROM map_user 
                                 WHERE Year = {year} AND Quarter = {quarter} GROUP BY State ORDER BY State;""")
                data6 = mycursor.fetchall()

                dff3 = pd.DataFrame(data6, columns = [i[0] for i in mycursor.description])

            dff3['State']=geo_state
            dff3['Registered_PhonePe_Users'] = dff3['Registered_PhonePe_Users'].astype(int)

            fig = px.choropleth(
                dff3,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='Registered_PhonePe_Users',
                hover_name='State',
                custom_data=['Registered_PhonePe_Users', 'PhonePe_App_Opens'],
                color_continuous_scale='rainbow')

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Registered PhonePe User = %{customdata[0]}<br>PhonePe App Opens = %{customdata[1]}')

            st.plotly_chart(fig)
#-----------------------------------------------/ Aggregated user /---------------------------------------------------------------------
            if year and quarter:

                mycursor.execute(f"""SELECT State, SUM(User_Count) AS User_Count FROM aggeregated_user 
                                 WHERE Year = 2018 AND Quarter = 1 GROUP BY State;""")
                data10 = mycursor.fetchall()

                dff4 = pd.DataFrame(data10, columns = [i[0] for i in mycursor.description])

            dff4['State']=geo_state
            dff4['User_Count'] = dff4['User_Count'].astype(int)

            fig1 = px.choropleth(
                dff4,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='User_Count',
                hover_name='State',
                custom_data='User_Count',
                color_continuous_scale='earth')

            fig1.update_geos(fitbounds="locations", visible=False)
            fig1.update_traces(hovertemplate='<b>%{hovertext}</b><br>User_Count = %{customdata[0]}')

            st.plotly_chart(fig1)

            if year and quarter and brand_state and brand:
                mycursor.execute(f"""SELECT Brand, User_Count FROM aggeregated_user 
                                WHERE Year = {year} AND Quarter = {quarter} AND State = '{brand_state}' ORDER BY User_count ASC;""")
                data12=mycursor.fetchall()  
                df12=pd.DataFrame(data12, columns= [i[0] for i in mycursor.description])
                new1=px.bar(df12,x = 'User_Count', y ='Brand', text='User_Count', color='User_Count', color_continuous_scale = 'thermal',
                             title = 'User Brand Analysis Chart', height = 600, orientation='h')
                new1.update_layout(title_font=dict(size=33), title_font_color='#6739b7')
                st.plotly_chart(new1, use_container_width=True)

            if state_button:
                bargraph4 = px.bar(df6, x ='State', y = 'Registered_User', text = 'Registered_User', color='Registered_User',
                            color_continuous_scale = 'thermal', title = 'Top 10 State Registered User Analysis Chart', height = 600)
                bargraph4.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph4,use_container_width=True)


            if district_button:
                bargraph5 = px.bar(df7, x ='District', y = 'Registered_User', text = 'Registered_User', color='Registered_User',
                            color_continuous_scale = 'thermal', title = 'Top 10 District Registered User Analysis Chart', height = 600)
                bargraph5.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph5,use_container_width=True)

            if pincode_button:
                newdf=df8
                newdf['Pincode'] = newdf['Pincode'].astype(str)
                bargraph6 = px.bar(newdf, x ='Pincode', y = 'Registered_User', text = 'Registered_User', color='Registered_User',
                            color_continuous_scale = 'thermal', title = 'Top 10 Postal Code Registered User Analysis Chart', height = 600)
                bargraph6.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
                st.plotly_chart(bargraph6,use_container_width=True)