import forum_scraper as fs
import streamlit as st
import pandas as pd

if 'forum' not in st.session_state:
    st.session_state.forum = ''
if 'search_terms' not in st.session_state:
    st.session_state.search_terms = ''
if 'num_results' not in st.session_state:
    st.session_state.num_results = 0
if 'tr_list' not in st.session_state:
    st.session_state.tr_list = []

def show_data(tr_list, sort_by, order):    
    tr_list_sorted = fs.get_sorted(tr_list, sort_by, order)    
    df = pd.DataFrame(
        {
            "title": fs.get_attributes(tr_list_sorted, 'title'),
            "url": fs.get_attributes(tr_list_sorted, 'url'),
            "key_phrases": fs.get_attributes(tr_list_sorted, 'phrases'),
            "views": fs.get_attributes(tr_list_sorted, 'views'),
            "likes": fs.get_attributes(tr_list_sorted, 'likes'),
            "date": fs.get_attributes(tr_list_sorted, 'date'),
            "replies": fs.get_attributes(tr_list_sorted, 'replies'),
        },
    )
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "title": "Title",
            "url": st.column_config.LinkColumn("URL"),
            "key_phrases": st.column_config.ListColumn("Key Phrases"),
            "views": "Views",
            "likes": "Likes",
            "date": "Date",
            "replies": "Replies",
        },
    )

st.title(':blue[Discourse Forum Scraper]')

col1, col2 = st.columns(2)
with col1:
    forum = st.selectbox(
        "Forum:",
        ("Monzo", "Emma", "Revolut", "Fintech Forum"))
    search_terms = st.text_input("Search terms:", value='credit card')
    if not search_terms:
        st.error("Please enter one or more search terms")
    num_results = st.number_input("Number of results:", min_value=1, max_value=100, value=5, step=1)
with col2:
    sort_by = st.selectbox(
        "Sort by:",
        ("Title", "Date", "Views", "Replies", "Likes"))
    order = st.selectbox(
        "Order:",
        ("Ascending", "Descending"))
    clicked = st.button("Start scrape")

if clicked:
    if (forum != st.session_state.forum or
        search_terms != st.session_state.search_terms or
        num_results != st.session_state.num_results):
        st.session_state.tr_list = fs.get_threads(forum, search_terms, num_results)
        st.session_state.forum = forum
        st.session_state.search_terms = search_terms
        st.session_state.num_results = num_results

    show_data(st.session_state.tr_list, sort_by, order)