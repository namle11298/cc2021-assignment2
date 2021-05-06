import boto3
from boto3.dynamodb.conditions import Key,Attr
def scan_subscription(email,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('subscription')
    response = table.scan(
        FilterExpression=Attr('email').eq(email)
    )
    print (response['Items'])
    return response['Items']
if __name__ == '__main__':
    scan_subscription('1')
