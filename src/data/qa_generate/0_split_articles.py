import polars as pl
import os

# Define the input and output paths
input_path = '../../../data/newspaper/old_korean_newspaper_economy_politic_min500char.csv'
output_dir = '../../../data/newspaper/economy_politic_split/train'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the CSV file
df = pl.read_csv(input_path)

# Calculate the number of files needed
num_rows = df.height
max_rows_per_file = 1000
num_files = (num_rows - 1) // max_rows_per_file + 1

# Split the dataframe and save to CSV files
for i in range(num_files):
    start_idx = i * max_rows_per_file
    end_idx = min((i + 1) * max_rows_per_file, num_rows)
    
    part_df = df.slice(start_idx, end_idx - start_idx)
    
    output_path = os.path.join(output_dir, f'old_korean_newspaper_economy_politic_min500char_{i+1}.csv')
    part_df.write_csv(output_path)

print(f"Split complete. {num_files} files created in {output_dir}")