import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('abcbook_list')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    

    if 'body' in event:
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            body = event['body']
    else:
        body = event
    
    print("Processed body:", json.dumps(body))
    
    body['id'] = str(uuid.uuid4())
    
    required_fields = ['Title', 'Authors', 'Year']
    missing_fields = [field for field in required_fields if field not in body or not body.get(field)]
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        print(error_msg)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_msg})
        }
    
    if isinstance(body.get('Authors'), str):
        body['Authors'] = [author.strip() for author in body['Authors'].split(',')]
    
    try:
        body['Year'] = int(body['Year'])
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Year must be a valid integer'})
        }
    
    try:
        # Attempt to add the item to DynamoDB
        table.put_item(Item=body)
        
        response = {
            'statusCode': 201,
            'body': json.dumps({'message': 'Book added successfully', 'id': body['id']})
        }
    except Exception as e:
        print(f"Error adding item to DynamoDB: {str(e)}")
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True
    }
    
    return response