import boto3
from decimal import Decimal
import json

def populate_music_table(song_list,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    for song in song_list['songs']:
        title = song['title']
        artist = song['artist']
        year = int(song['year'])
        web_url = song['web_url']
        image_url = song['img_url']
        print('Adding song: ',title)
        table.put_item(Item={
                'title': title,
                'artist': artist,
                'year': year,
                'web_url': web_url,
                'image_url': image_url
            })

if __name__ == '__main__':
    with open('a2.json') as json_file:
        song_list = json.load(json_file,parse_float=Decimal)
    populate_music_table(song_list)