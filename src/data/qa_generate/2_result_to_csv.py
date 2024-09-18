import csv
import json

import pandas as pd
import os

model = "gpt-4o-mini"

output_path = '../../../data/newspaper/economy_politic_qa'
############################################################
# Loading data from saved file

file_number = 1

batch_result = []
batch_response_file_name = os.path.join(output_path, 'response', f'old_korean_newspaper_economy_politic_min500char_{file_number}.jsonl')
result_file_name = os.path.join(output_path, f'old_korean_newspaper_economy_politic_min500char_{file_number}.csv')

with open(batch_response_file_name, 'r') as file:
    for line in file:
        json_object = json.loads(line.strip())
        batch_result.append(json_object)

############################################################
# Reading only the first batch results
print('\n### Reading the batch results')

rows = []
for res in batch_result:
    # Getting index from task id
    task_id = res['custom_id']
    index = task_id.split('-')[-1]
    result = res['response']['body']['choices'][0]['message']['content']
    
    split_qa = result.split("Answer:")
    question = split_qa[0].replace("Question:", "").strip()
    answer = split_qa[1].strip()
    
    dict1 = {'Question': question, 'Answer': answer}
    rows.append(dict1)

print('\n------------------------')

results_df = pd.DataFrame(rows)

results_df.to_csv(result_file_name, index=False)
print(f'\n### Saved the results to {result_file_name}')
