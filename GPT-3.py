import os
import openai
import json
import time
from jsonlines import jsonlines
# Load your API key from an environment variable or secret management service

openai.api_key = ("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")

file_name = "gpt3training.txt"

with open(file_name) as f:
    mylist = f.read().splitlines()

json_to_upload = json.dumps([{'text': test} for test in mylist], default=str, indent=1)
json_to_upload = json.loads(json_to_upload)
print(type(json_to_upload))
# json_to_upload = json.dumps([{'text': mylist}], default=str, indent=1)
# json_to_upload = json.loads(json_to_upload)

with jsonlines.open('upload.jsonl', mode='w') as writer:
    for entry in json_to_upload:
        writer.write(entry)

upload = openai.File.create(
    file=open("upload.jsonl"),
    purpose='answers'
)

print(upload['id'])

#  print(openai.File.list())

time.sleep(10)

response = openai.Answer.create(
    search_model="ada",
    model="curie",
    question="Why don’t you like this product?",
    file=upload['id'],
    examples_context="In 2017, U.S. life expectancy was 78.6 years. With a 2019 population of 753,675, it is the largest city in both the state of Washington and the Pacific Northwest",
    examples=[["What is human life expectancy in the United States?", "78 years."],
              ["what is the population of Seattle?", "Seattle's population is 724,305"]],
    max_tokens=40,
    stop=["\n", "<|endoftext|>"],
)

print(response)

time.sleep(10)

openai.File.delete(upload['id'])
