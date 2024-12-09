import pandas as pd
import boto3
import json
import time

AWS_ACCESS_KEY = "your-aws-access-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-access-key"
AWS_SESSION_TOKEN = "your-aws-session-token"

def stream_data(df, stream_name, region):
    # Initialize a Kinesis client
    kinesis_client = boto3.client(
        'kinesis',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=region # or your preferred region
    )
    
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Convert the row to a dictionary and then to JSON
        record = row.to_dict()
        json_record = json.dumps(record)
        
        # Send the JSON record to the Kinesis Data Stream
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json_record,
            PartitionKey=f"{str(row['STN Code'])}_{str(row['Year'])}"  # Use a unique key like STN Code
        )
        print(f"Record {index} sent with response: {response}")
        time.sleep(2)

# Read the CSV file
df = pd.read_csv("./water_data_final.csv")

# Call the stream_data function
stream_name = "your-kinesis-stream-name"  # Replace with your Kinesis stream name
region = "us-east-1"  # Replace with your AWS region
stream_data(df, stream_name, region)
