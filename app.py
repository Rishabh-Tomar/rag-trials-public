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
                    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAw0AAADNCAMAAADNP2z7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAIHUExURWmm0EqWyTaLxCaDwRh7vglzukGRx1GZy3Kr00aTyB1+vx9/vzSKxFKay1qezSqFwjiMxW6p0q/L4V2gzmun0U2XyiKAwHWs0yB/v0eUyVufzVmezTKJxF6hzk6YyhV5vVaczKPF3myo0RF3vCGAwEiVyTCIw3et1C2GwjOJxDWKxFidzIi32D+QxzeMxUOSyB5+vxp8vn+y1SmEwQ52uzqNxUCQxzGIwxV6vZvB3FyfzWqn0WKizyuFwhZ6vcva50yXygx0uxJ4vJC72ieDwQpzuhR5vBB3vBx9vjyOxnGr0hN4vCOBwMzb6MbY5sjZ53qv1MjZ5juOxhl8vmCizkaUyGak0At0umSjz4+72Xat0yWCwW+q0m2o0c3b6Gim0EmVyXmv1CyGwoK01sfY5iWCwC6Gw3iu1FWbzBt8vi+Hw8XX5kKRxySBwKLF3n6x1Q11u0WTyHOr07/U5GOjz7/U5T6PxlCZy1Oay3Cq0mGizyiEwcDV5VedzE+Yym6p0V+hzsTX5nSs07rR40SSyLPO4jmNxarJ4Huw1S6Hw3yw1Za+25G82mal0A92uzaLxY+62ZO92neu1JnA3D2PxlSby5/D3Rd7vZ7C3R19v5rA3J3C3afH36jI363K4LLN4b7T5EuWyWel0Mra516gzmWkz4e22JS92qDE3avJ4LDM4bjQ4wAAAJACl+4AAACtdFJOU/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8A/UUE8AAAAAlwSFlzAAAOwwAADsMBx2+oZAAAH+dJREFUeF7tnfmj3cR1x8FwAWOzFTBrjIvZKYsLAcIWTDEYcNpXszhhKZAGDARaQ6kpUEJKCSVpgTaBUrqTkq73j6x05jOakTQjaaTRfc955/ODPXPO0ZHuffreWTSSjlsq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" class="mr-3 h-16 w-fit" alt="NTT DATA Logo">
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

