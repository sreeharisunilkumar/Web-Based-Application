import json
import boto3
import base64

s3 = boto3.client('s3')
BUCKET_NAME = 'aws-abcbooks-web-bkt'

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {})
        if not query_params:
            raise ValueError("No query parameters provided")
        
        image_key = query_params.get('key')
        if not image_key:
            raise ValueError("No 'key' parameter provided")
        

        print(f"Image key: {image_key}")
        
        response = s3.get_object(Bucket=BUCKET_NAME, Key=image_key)
        

        image_content = response['Body'].read()
        

        content_type = response.get('ContentType', 'application/octet-stream')
        

        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": content_type,
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
            },
            "body": encoded_image,
            "isBase64Encoded": True
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
            },
            "body": json.dumps({"error": str(e)})
        }
