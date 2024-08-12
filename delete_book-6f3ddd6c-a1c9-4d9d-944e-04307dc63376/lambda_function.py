import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('abcbook_list')

def lambda_handler(event, context):
    # Add CORS headers to all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,DELETE'
    }

    # Handle preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({})
        }

    try:
        book_id = event['pathParameters']['id']
        
        response = table.delete_item(
            Key={'id': book_id},
            ReturnValues='ALL_OLD'
        )
        

        if 'Attributes' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'message': 'Book not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Book deleted successfully'})
        }
    except KeyError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Missing book ID in the request'})
        }
    except ClientError as e:
        print(f"DynamoDB ClientError: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Failed to delete book from database'})
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'An unexpected error occurred'})
        }