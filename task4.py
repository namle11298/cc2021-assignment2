import boto3
from decimal import Decimal
import json
import requests

def upload_image(song_list,s3=None):
    if not s3:
        client = boto3.client('s3', region_name='us-east-1')
    for song in song_list['songs']:
        title = song['title']
        image_url = song['img_url']
        img_data = requests.get(image_url,stream=True)
        client.upload_fileobj(img_data.raw, "music-image-assignment2",
         title.split('/')[-1],ExtraArgs={'ContentType': 'image/jpeg'})
if __name__ == '__main__':
    with open('a2.json') as json_file:
        song_list = json.load(json_file,parse_float=Decimal)
    upload_image(song_list)