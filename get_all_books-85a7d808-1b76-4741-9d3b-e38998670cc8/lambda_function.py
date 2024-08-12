import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('abcbook_list')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        print("Starting Lambda function execution")
        
        # Scan the table to get all items
        response = table.scan()
        print("DynamoDB scan response:", response)
        
        # Extract the items from the response
        items = response.get('Items', [])
        print("Extracted items:", items)
        
        # Return the items without generating presigned URLs
        return {
            'statusCode': 200,
            'body': json.dumps(items, default=decimal_default)
        }
    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
