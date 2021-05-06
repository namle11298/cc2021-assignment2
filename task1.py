from pprint import pprint

import boto3

def put_login(email, user_name, password, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('login')
        response = table.put_item(
            Item={
                'email': email,
                'user_name': user_name,
                'password': password
            }
        )
        return response

if __name__ == '__main__':
    student_id = "s3625204"
    orginial_user_name = "Nam Le"
    for i in range(10):
        email = student_id + str(i) + "@rmit.edu.vn"
        user_name = orginial_user_name + str(i)
        password = ""
        for x in range(6):
            counter = x + i
            if counter > 9:
                counter = counter - 10
            password = password+str(counter)
        login_resp = put_login(email, user_name, password)

    print("Put login succeeded:")

    pprint(login_resp, sort_dicts=False)