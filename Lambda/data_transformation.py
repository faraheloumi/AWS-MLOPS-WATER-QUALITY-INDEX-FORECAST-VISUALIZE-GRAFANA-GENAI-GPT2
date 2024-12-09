import json
import boto3
import base64
import datetime

def validate_and_transform_record(payload):
    """
    Validate and transform the incoming record payload.
    """
    processed_payload = payload.copy()
    try:
        # Required fields
        required_fields = ['STN Code', 'Dissolved Oxygen', 'Location Name', 'Year', 
                           'pH', 'Conductivity', 'BOD', 'Nitrate N + Nitrite N', 
                           'Fecal Coliform', 'Total Coliform', 'WQI', 'lat', 'lon']
        
        # Check for missing fields
        for field in required_fields:
            if field not in processed_payload or processed_payload[field] is None:
                print(f"Missing or null field: {field} in {processed_payload['STN Code']}_{processed_payload['Year']}")
        
        # Data type validation and transformation
        # processed_payload['Year'] = int(processed_payload['Year'])
        processed_payload['Dissolved Oxygen'] = float(processed_payload['Dissolved Oxygen'])
        processed_payload['pH'] = float(processed_payload['pH'])
        processed_payload['Conductivity'] = float(processed_payload['Conductivity'])
        processed_payload['BOD'] = float(processed_payload['BOD'])
        processed_payload['Nitrate N + Nitrite N'] = float(processed_payload['Nitrate N + Nitrite N'])
        processed_payload['Fecal Coliform'] = int(processed_payload['Fecal Coliform'])
        processed_payload['Total Coliform'] = int(processed_payload['Total Coliform'])
        processed_payload['WQI'] = float(processed_payload['WQI'])
        processed_payload['lat'] = float(processed_payload['lat'])
        processed_payload['lon'] = float(processed_payload['lon'])
        
        # Range checks
        if not (0 <= processed_payload['pH'] <= 14):
            print(f"Invalid pH value: {processed_payload['pH']}")
        if not (-90 <= processed_payload['lat'] <= 90):
            print(f"Invalid latitude: {processed_payload['lat']}")
        if not (-180 <= processed_payload['lon'] <= 180):
            print(f"Invalid longitude: {processed_payload['lon']}")
        
        # Add metadata
        processed_payload['processed_timestamp'] = datetime.datetime.utcnow().isoformat()

        # Omit unwanted fields
        processed_payload.pop('Year', "unknown")       # Remove 'Year' if it exists
        processed_payload.pop('STN Code', "unknown")  # Remove 'STN Code' if it exists
        print(f"Final Payload for S3: {payload}")
        return processed_payload
    except Exception as e:
        print(f"Validation/Transformation error: {e}")
        return payload

def lambda_handler(event, context):
    # Initialize the S3 client
    s3 = boto3.client('s3')
    bucket_name = 'your-bucket-name'
    
    for record in event['Records']:
        try:
            print(f"Processed Kinesis Event - EventID: {record['eventID']}")
            
            # Decode the base64-encoded record data
            record_data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            payload = json.loads(record_data)
            print(f"Raw Record Data: {payload}")
            
            # Validate and transform the payload
            processed_payload = validate_and_transform_record(payload)
            print(f"Validated/Transformed Record: {processed_payload}")

            # Prepare file name and content
            file_name = (
                f"water_data/"
                f"year={payload['Year']}/"
                f"stn_code={payload['STN Code']}/"
                f"record_{record['eventID']}.json"
            )
            print(f"File Name: {file_name}")
            file_content = json.dumps(processed_payload)  # Convert the payload dictionary to a JSON string
            
            # Upload to S3
            s3.put_object(
                Body=file_content.encode('utf-8'), 
                Bucket=bucket_name, 
                Key=file_name
            )
            print(f"File uploaded: {file_name}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    print(f"Successfully processed {len(event['Records'])} records.")
    return {
        'statusCode': 200,
        'body': 'Files uploaded successfully.'
    }
