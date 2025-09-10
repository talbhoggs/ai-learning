import os
import streamlit as sl
#if not os.environ.get("WATSONX_APIKEY"):
#  os.environ["WATSONX_APIKEY"] = getpass.getpass("Enter API key for IBM watsonx: ")
# https://cloud.ibm.com/apidocs/watsonx-ai#introduction

from langchain_ibm import ChatWatsonx

project_id = os.environ["WATSONX_PROJECT_ID"]
model = ChatWatsonx(
    model_id="meta-llama/llama-3-2-3b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=project_id
)

sl.title("Ask anything ? ")

question = sl.text_input("Enter Question : ")

if question:
    response = model.invoke(question)
    sl.write(response.content)