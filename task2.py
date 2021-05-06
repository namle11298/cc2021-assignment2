import boto3
from decimal import Decimal
import json
TABLE_NAME='music'
def create_music_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        dynamodb_client = boto3.client('dynamodb')
    existing_tables = dynamodb_client.list_tables()['TableNames']
    if TABLE_NAME not in existing_tables:
        music_table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName':'title',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName':'artist',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName':'title',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName':'artist',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print("Table created!")
    else:
        print("Table already exists")

if __name__ == '__main__':
    with open('a2.json') as json_file:
        song_list = json.load(json_file,parse_float=Decimal)
    create_music_table()