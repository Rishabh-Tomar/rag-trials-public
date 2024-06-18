import pandas as pd
import streamlit as st
from streamlit_tailwind import st_tw
from llm_wrapper import llm
from helpers import get_metadata_of_df
import os



st.set_page_config(
    page_icon="favicon.svg", layout="wide", page_title="AI for Analytics"
)
# Hide menu and footer
hide_streamlit_style = """
            <style>
            header { display: none !important; }
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            .appview-container .main .block-container{ padding-top: 0rem; }
            .stMarkdown div { margin-bottom: 0rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st_tw(
    text="""
    <nav class="fixed z-30 w-full py-3 px-4 ">
        <div class="flex justify-between items-center max-w-screen-2xl mx-auto">
            <div class="flex justify-start items-center">
                <div class="flex mr-14">
                    <img src="/app/static/logo.png" class="mr-3 h-16 w-fit" alt="NTT DATA Logo">
                    <span class="self-center flex text-xl font-semibold whitespace-nowrap dark:text-[#fafafa]">Answerlytics - AI For Analytics</span>
                </div>
            </div>
        </div>
    </nav>
            """,
    height=70,
    key="header",
)


available_models = {
    "Chat GPT-4o": "gpt-4o",
    "Chat GPT-4 Turbo": "gpt-4-turbo",
    "Chat GPT-3.5 Turbo": "gpt-3.5-turbo",
}

# List to hold datasets
if "datasets" not in st.session_state:
    datasets = {}
    st.session_state["datasets"] = datasets
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]

key_col1, key_col2 = st.columns(2)
model_name_col = key_col2

if "OPENAI_API_KEY" not in os.environ:
    openai_key = key_col1.text_input(
        label=":key: OpenAI Key:",
        type="password",
        value="",
    )
else:
    openai_key = os.getenv("OPENAI_API_KEY")
    model_name_col = key_col1

model_name = model_name_col.selectbox(
    label=":brain: Select a Model:", options=list(available_models.keys())
)

chosen_dataset = "custom"

try:
    uploaded_file = st.file_uploader(":computer: Load a CSV file:", type="csv")
    index_no = 0
    if uploaded_file:
        # Read in the data, add it to the list of available datasets. Give it a nice name.
        file_name = uploaded_file.name[:-4].capitalize()
        datasets[chosen_dataset] = pd.read_csv(uploaded_file)
        # We want to default the radio button to the newly added dataset
        index_no = len(datasets) - 1
except Exception as e:
    st.error("File failed to load. Please select a valid CSV file.")
    print("File failed to load.\n" + str(e))

if chosen_dataset in datasets:
    with st.expander("Data Set"):
        st.metric("Totl Rows", datasets[chosen_dataset].shape[0])
        tabs = st.tabs(["Metadata", "Data"])
        with tabs[0]:
            st.subheader("Meta Data")
            st.write(get_metadata_of_df(datasets[chosen_dataset]))
        with tabs[1]:
            st.subheader("Data")
            st.write(datasets[chosen_dataset])

    # Text area for query
    query = st.text_area("What would you like to know?", height=10)
    go_btn = st.button("Go...")

    selected_model_value = available_models[model_name]

    # Execute chatbot query
    if go_btn:
        api_keys_entered = True
        # Check API keys are entered.
        if model_name in ("ChatGPT-4", "ChatGPT-3.5", "GPT-3", "GPT-3.5 Instruct"):
            if not openai_key.startswith("sk-"):
                st.error("Please enter a valid OpenAI API key.")
                api_keys_entered = False
        if api_keys_entered:
            # Create model, run the request and print the results
            try:                
                call_llm = llm(selected_model_value, openai_key, datasets[chosen_dataset])
                
                # Run the question                
                gptResult = call_llm.run_query(query)
                st.markdown(gptResult, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("Ran into error. (" + str(e) + ")")

