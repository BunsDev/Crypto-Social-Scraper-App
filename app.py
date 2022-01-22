import datetime
import pandas as pd
import streamlit as st
import json
from streamlit_app.ui import (
    get_social_links_html,
    get_social_links_data,
    get_market_data,
    get_community_data,
    get_cg_summary_data,
)
import streamlit.components.v1 as components
from streamlit_app.utils import get_description, load_coingecko_data, get_repo_data
from streamlit_app.dashboard import body
from pathlib import Path

st.set_page_config(layout="wide")  # this needs to be the first Streamlit command called

left_col, right_col = st.columns(2)
## Basic setup and app layout
with left_col:
    st.title("Crypto Social Analysis App")
    st.markdown(
        "*Check out the methodology walk-through "
        "[here](https://www.crosstab.io/articles/staged-rollout-analysis) and Streamlit "
        "app mechanics [here](https://www.crosstab.io/articles/streamlit-review).*"
    )

### LOAD DATA
# Load 10,000 rows of data into the dataframe.
loading_data_container = st.sidebar.empty()
loading_data_container.info("Loading data...")
data = load_coingecko_data()
loading_data_container.success("Loading data...done!")
loading_data_container.empty()


### SIDEBAR
st.sidebar.title("Select which Cryptocurrency you'd like to look into!")
coin_choice = st.sidebar.selectbox("Pick a coin", data.name.tolist())
image_link = data.loc[data.name == str(coin_choice), "image"][0].get("small", "")
st.sidebar.markdown(f"![]({image_link})")

## HIGH LEVEL STATS
with left_col:
    st.markdown(f"## Coin Info | ![]({image_link})")
    ### Description
    description_text = get_description(data, coin_choice)
    lef_expander1 = st.expander("Coin Description")
    with lef_expander1:
        st.markdown(description_text, unsafe_allow_html=True)
    left_expander2 = st.subheader("CoinGecko Stats")
    get_cg_summary_data(coin_choice, data)


##Summary Stats
with right_col:
    st.markdown(f"# Summary Stats")
    ### Market Data
    st.markdown(f"### Market Data")
    market_data = get_market_data(coin_choice, data)
    for stat in market_data.items():
        st.markdown(
            f"<p class='small-font'>{stat[1][1]} <strong>{stat[0]}</strong>: {stat[1][0]}</p>",  # noqa: E501
            unsafe_allow_html=True,
        )

    ### Social Data
    st.markdown(f"### Social Data / Links")
    components.html(str(get_social_links_html(coin_choice, data)))
    community_data = get_community_data(coin_choice, data)
    for stat in community_data.items():
        st.markdown(
            f"<p class='small-font'>{stat[1][1]} <strong>{stat[0]}</strong>: {stat[1][0]}</p>",  # noqa: E501
            unsafe_allow_html=True,
        )

links_dict = get_social_links_data(coin_choice, data)
repo_link_choice = (
    links_dict["github"]
    if isinstance(links_dict["github"], list)
    else list(links_dict["github"])
)
repo_choice = st.selectbox("Select a repo", repo_link_choice)
input_type = st.radio(
    "Filter Repo Commits",
    (
        "Filter commits by Date",
        "Filter commits by n",
        "Don't filter commits (large repos make take time)",
    ),
)

if input_type == "Filter commits by Date":
    filter_option = st.date_input(
        "Pulling repository commits from: (default 2021-01-01)",
        datetime.date(2021, 1, 1),
    )
    d = datetime.datetime.combine(filter_option, datetime.datetime.min.time())
elif input_type == "Filter commits by n":
    filter_option = st.number_input(
        "Pull the first `n` commits", min_value=1, max_value=None, value=100
    )
elif input_type == "Filter commits by n":
    filter_option = None
git_container = st.empty()
with git_container:
    git_container.title("Git Repository Overview")
    second_container = git_container.container()
    with st.form(key="my_form_to_submit"):
        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            if input_type == "Filter commits by Date":
                commit_history = get_repo_data(
                    repo_choice, since=d
                )  # d.strftime("%Y-%m-%d")
            elif input_type == "Filter commits by n":
                commit_history = get_repo_data(
                    repo_choice, first_n_commits=filter_option
                )

            body = body(commit_history, second_container)


# rel_cols = ['symbol', 'name', 'genesis_date', 'sentiment_votes_up_percentage',
#        'sentiment_votes_down_percentage', 'market_cap_rank', 'coingecko_rank',
#        'coingecko_score', 'developer_score', 'community_score',
#        'liquidity_score', 'public_interest_score', 'last_updated',
#        'contract_address']

# st.dataframe(data[rel_cols])