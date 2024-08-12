import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('abcbook_list')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    http_method = event.get('httpMethod')
    
    if http_method == 'PUT':
        return update_book(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported HTTP method'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT'
            }
        }

def update_book(event):
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError:
        body = event['body']
    
    book_id = event['pathParameters']['id']
    
    update_expression = "set "
    expression_attribute_values = {}
    expression_attribute_names = {}
    
    for key, value in body.items():
        if key != 'id':  # Prevent updating the id
            update_expression += f"#{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
            expression_attribute_names[f"#{key}"] = key
    
    update_expression = update_expression.rstrip(", ")
    
    try:
        response = table.update_item(
            Key={'id': book_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="UPDATED_NEW"
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Book updated successfully', 'updatedAttributes': response['Attributes']}, cls=DecimalEncoder),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT'
            }
        }


def add_cors_headers(response):
    if 'headers' not in response:
        response['headers'] = {}
    response['headers']['Access-Control-Allow-Origin'] = '*'
    response['headers']['Access-Control-Allow-Headers'] = 'Content-Type'
    response['headers']['Access-Control-Allow-Methods'] = 'OPTIONS,PUT'
    return response


def cors_wrapped_handler(event, context):
    response = lambda_handler(event, context)
    return add_cors_headers(response)