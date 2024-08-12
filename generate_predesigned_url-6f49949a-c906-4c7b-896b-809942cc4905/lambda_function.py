import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('abcbook_list')  # Replace with your actual table name
BUCKET_NAME = 'aws-abcbooks-web-bkt'  # Replace with your actual S3 bucket name

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # Log the entire event for debugging
        
        if event.get('queryStringParameters') and 'key' in event['queryStringParameters']:
            return get_presigned_url(event, context)
        elif event.get('pathParameters') and 'id' in event['pathParameters']:
            return get_book(event, context)
        else:
            raise ValueError("Invalid request: missing required parameters")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_presigned_url(event, context):
    try:
        image_key = event['queryStringParameters']['key']
        if not image_key:
            raise ValueError("No 'key' provided in query parameters")
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': image_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'url': presigned_url})
        }
    except Exception as e:
        print(f"Error in get_presigned_url: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_book(event, context):
    try:
        book_id = event['pathParameters']['id']
        book = get_book_from_dynamodb(book_id)
        
        if 'ImageUrl' in book and book['ImageUrl']:
            image_key = book['ImageUrl']
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': image_key},
                ExpiresIn=3600  # URL expires in 1 hour
            )
            book['ImageUrl'] = presigned_url
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(book, cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error in get_book: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_book_from_dynamodb(book_id):
    try:
        response = table.get_item(Key={'id': book_id})
        if 'Item' in response:
            return response['Item']
        else:
            raise ValueError(f"Book with id {book_id} not found")
    except ClientError as e:
        print(f"DynamoDB error: {e.response['Error']['Message']}")
        raise
