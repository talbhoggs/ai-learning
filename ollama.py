
from langchain_community.chat_models import ChatOllama
import streamlit as sl

model = ChatOllama(model="llama3.2") 
sl.title("Ask anything ? ")

question = sl.text_input("Enter Question : ")

if question:
    response = model.invoke(question)
    sl.write(response.content)