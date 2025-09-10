#import getpass
import os

#if not os.environ.get("WATSONX_APIKEY"):
#  os.environ["WATSONX_APIKEY"] = getpass.getpass("Enter API key for IBM watsonx: ")
# https://cloud.ibm.com/apidocs/watsonx-ai#introduction

from langchain_ibm import ChatWatsonx

WATSONX_PROJECT_ID = os.environ["WATSONX_PROJECT_ID"]
model = ChatWatsonx(
    #model_id="meta-llama/llama-4-2-3b-instruct",
    model_id="meta-llama/llama-3-3-70b-instruct",
    #model_id="ibm/granite-3-8b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=WATSONX_PROJECT_ID
)

question = input("Enter question? ")
response = model.invoke(question)
print(response.content)