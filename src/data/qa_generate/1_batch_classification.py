import json
import os
import time
from datetime import datetime

import pandas as pd
from openai import OpenAI

model = "gpt-4o-mini"

input_path = '../../../data/newspaper/economy_politic_split/train'
output_path = '../../../data/newspaper/economy_politic_qa/train'

os.makedirs(output_path, exist_ok=True)
os.makedirs(os.path.join(output_path, 'request'), exist_ok=True)
os.makedirs(os.path.join(output_path, 'response'), exist_ok=True)

file_number = 1

# articles_path = os.path.join(input_path, f'test.csv')
articles_path = os.path.join(input_path, f'old_korean_newspaper_economy_politic_min500char_{file_number}.csv')
batch_request_file_name = os.path.join(output_path, 'request', f'old_korean_newspaper_economy_politic_min500char_{file_number}.jsonl')
batch_response_file_name = os.path.join(output_path, 'response', f'old_korean_newspaper_economy_politic_min500char_{file_number}.jsonl')
articles_df = pd.read_csv(articles_path)

# print(keywords_df['keyword'][:5])
# print(categories[:5])

############################################################
system_prompt = '''대한제국 시기 기사를 분석해서 역사적인 관점에서 하나의 QUESTION & ANSWER 쌍을 만들어줘. 응답은 한국어로 해줘. 그리고 Question: Answer: 를 분명하게 구분해줘'''

############################################################
# Creating an array of json tasks

tasks = []

for index, line in articles_df.iterrows():
    article = line['dcterms:abstract']

    task = {
        "custom_id": f'{index}',
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "temperature": 0.1,
            # "response_format": {
            #     "type": "json_object"
            # },
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": article
                }
            ],
        }
    }
    # print(task)
    tasks.append(task)

############################################################
# Create an OpenAI client

client = OpenAI()

############################################################
# Creating a batch tasks file


with open(batch_request_file_name, 'w') as file:
    for task in tasks:
        file.write(json.dumps(task) + '\n')

############################################################
# Uploading the batch tasks file

batch_file = client.files.create(
    file=open(batch_request_file_name, "rb"),
    purpose="batch"
)
print(batch_file)

############################################################
# Creating the batch job

batch_job = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)
print(batch_job)

############################################################
# Checking the batch status

batch_job_id = batch_job.id

while batch_job.output_file_id is None and batch_job.errors is None:
    batch_job = client.batches.retrieve(batch_job_id)
    print(f'## output_file_id: {batch_job.output_file_id}, errors: {batch_job.errors}')

    if batch_job.output_file_id is None and batch_job.errors is None:
        print("---- Current Time:", datetime.now())
        # Sleep for 1 minute (60 seconds)
        time.sleep(60)

############################################################
# Retrieving results

result_file_id = batch_job.output_file_id # 예시: 'file-87wNVt8YwigtVZJ24EGIoLWI'

if result_file_id:
    result = client.files.content(result_file_id).content

    with open(batch_response_file_name, 'wb') as file:
        file.write(result)

    print(f"\nCreated a file: data/batch_job_results_{model}.csv")
