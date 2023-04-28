import os
from langchain.llms import OpenAI

if not os.environ.get("OPENAI_API_KEY"):
    raise Exception("Please set your OpenAI API key as an environment variable.")

llm = OpenAI(temperature=0.9)

text = "What is the meaning of life?"

print(llm(text))
