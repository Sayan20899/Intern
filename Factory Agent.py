import pandas as pd
from io import StringIO
from pprint import pprint

url = "https://raw.githubusercontent.com/Sayan20899/OpenData4Manufacturing/master/OpenData4Manufacturing/Batches/120P5F_60T28U_1c/s1.csv"


# Specify column names
column_names = ['arrival_time', 'job_id', 'family_type', 'priority']

# Read the CSV data into a DataFrame without the extra column
df = pd.read_csv(url, header=None, sep=';', usecols=[0, 1, 2, 3])

# Assign column names to the DataFrame
df.columns = column_names

# Convert DataFrame to dictionary
data_dict = df.to_dict(orient='index')

# Convert the dictionary keys to be row numbers starting from 1
output_dict = {i+1: row for i, row in data_dict.items()}

# Print the output dictionary
pprint(output_dict)
