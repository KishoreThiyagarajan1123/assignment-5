import os
import requests
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
from sqlalchemy import create_engine
import plotly.express as px



API_TOKEN = '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'

headers = {"Authorization": f"token {API_TOKEN}"}


def fetch_github_data(query, sort_by="stars", order="desc"):
    url = f"https://api.github.com/search/repositories?q={query}&sort={sort_by}&order={order}&per_page=100"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repos = response.json()["items"]
        data_list = []
        
        for repo in repos:
            data = {
                'RepositoryName': repo['name'],
                'OwnerName': repo['owner']['login'],
                'Description': repo.get('description', 'No description'),
                'URL': repo['html_url'],
                'ProgrammingLanguage': repo.get('language', 'Not specified'),
                'Creation Date': repo['created_at'],
                'LastUpdate': repo['updated_at'],
                'Stars': repo['stargazers_count'],
                'Forks': repo['forks_count'],
                'OpenIssues': repo['open_issues_count'],
                'License': repo['license']['name'] if repo['license'] else 'No license'
            }
            data_list.append(data)
        
        return data_list
    else:
        st.error(f"Failed to fetch data from GitHub: {response.status_code}")
        return []


st.title("GitHub Data Dive")
st.subheader("Explore GitHub repositories for trending topics in the data world.")

with st.sidebar:
  select=option_menu('Main Menu',['Upload & Extracting','Data Visualization'])


if select=='Upload & Extracting':

        topic = st.text_input("Enter a topic to search for repositories")

        
        if 'df' not in st.session_state:
            st.session_state['df'] = None  

        
        if st.button("Fetch Repositories"):
            if topic:
                repo_data = fetch_github_data(topic)
                
                if repo_data:
                    df = pd.DataFrame(repo_data)
                    st.session_state['df'] = df  
                    st.dataframe(df) 
                    st.success(f"Fetched {len(df)} repositories for the topic '{topic}'")
                else:
                    st.warning("No data fetched. Try a different topic.")
            else:
                st.warning("Please enter a search topic.")

        
        if st.button('Save to database'):
            if st.session_state['df'] is not None:
                df = st.session_state['df']
                
                
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='root',
                    database='youtube'
                )

                cursor = connection.cursor()

                
                engine = create_engine("mysql+mysqlconnector://root:root@localhost/youtube")
                
                
                df.to_sql('gitshub', con=engine, if_exists='append', index=False)

                
                connection.commit()

        
                cursor.close()
                connection.close()

                st.info('Data saved to database successfully!')
            else:
                st.warning("No data to save. Please fetch repositories first.")

if select=='Data Visualization':
        db=mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='youtube'

        )
        mycursor= db.cursor()


        
        query1 = 'select ProgrammingLanguage,Stars,Forks,OpenIssues From gitshub'
        mycursor.execute(query1)
        t1=mycursor.fetchall()
        mf1= pd.DataFrame(t1,columns=['Programming Language','Stars','Forks','OpenIssues'])
        
        mfs1=mf1.groupby('Programming Language')[['Stars','Forks','OpenIssues']].sum()
        mfs1.reset_index(inplace=True)
        

    
        fig2=px.bar(mfs1,x='Programming Language',y='Stars',title='No of Stars')
        st.plotly_chart(fig2, use_container_width=True)
            
        fig3=px.bar(mfs1,x='Programming Language',y='Forks',title='No of Forks',color_discrete_sequence=px.colors.sequential.Agsunset_r)
        st.plotly_chart(fig3, use_container_width=True)
            
        fig4=px.bar(mfs1,x='Programming Language',y='OpenIssues',title='No of open issues',color_discrete_sequence=px.colors.sequential.Agsunset_r)
        st.plotly_chart(fig4, use_container_width=True)    
        
