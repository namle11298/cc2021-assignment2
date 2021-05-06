import datetime
import boto3

from boto3.dynamodb.conditions import Key,Attr
from flask import Flask, render_template, url_for, redirect, request, session,flash

app = Flask(__name__)
app.secret_key = 'cc2021'
@app.route('/', methods=['POST','GET'])
def root():
    login_error = None
    if request.method == 'POST':
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        if user_email == '' or user_password =='':
            login_error = 'email or password is invalid'
            return render_template('index.html',error=login_error)
        user = query_login(user_email,user_password)
        if len(user) != 1:
            login_error = 'email or password is invalid'
            return render_template('index.html',error=login_error)
        else:
            user = query_email(user_email)
            session['login'] = True
            session['email'] = user[0]['email']
            session['user_name'] = user[0]['user_name']
            return redirect(url_for("main"))
    else:
        if 'login' in session:
            if session['login'] == True:
                return redirect(url_for("main"))
            else:
                return render_template('index.html')
        else:
            return render_template('index.html')

@app.route('/register',methods=['POST','GET'])
def register():
    register_error = None
    session['login'] = False
    session.pop('user_name',None)
    session.pop('email', None)
    if request.method == 'POST':
        user_email = request.form.get("email")
        user_name = request.form.get("user_name")
        user_password = request.form.get("password")
        if (len(query_email(user_email)) != 0):
            register_error = 'The email already exists'
            return render_template('register.html',error=register_error)
        else:
            add_login(user_email,user_password,user_name)
            flash('You can now log in with your new email and password')
            return redirect(url_for("root"))
    else:
        return render_template('register.html')

@app.route('/main', methods=['POST','GET'])
def main():
    main_error = None
    empty_query = None
    if request.method == 'POST':
        if request.form['submit-button'] == 'query':
            song_title = request.form.get("title")
            song_year = request.form.get("year")
            song_artist = request.form.get("artist")
            scan_result = scan_song(song_title,song_year,song_artist)
            song_image = []
            for i in scan_result:
                song_image.append(create_presigned_url('music-image-assignment2',i['title']))
            if len(scan_result) == 0:
                empty_query = 'No result is  retrieved. Please query again'
            subscribed_song = scan_subscription(session['email'])
            subscribed_song_image = []
            for song in subscribed_song:
                subscribed_song_image.append(create_presigned_url('music-image-assignment2',song['title']))
            return render_template('main.html',user_name=session['user_name'],song=scan_result,len=len(scan_result),len2=len(subscribed_song),image=song_image,empty_query=empty_query,
                subscribed_image=subscribed_song_image,subscribed_song=subscribed_song)
        elif request.form['submit-button'] == 'subscribe':
            song_title = request.form.get("title")
            song_artist = request.form.get("artist")
            subscribe_song(song_title,song_artist)
            subscribed_song = scan_subscription(session['email'])
            subscribed_song_image = []
            for song in subscribed_song:
                subscribed_song_image.append(create_presigned_url('music-image-assignment2',song['title']))
            return render_template('main.html',user_name=session['user_name'],len=0,subscribed_image=subscribed_song_image,subscribed_song=subscribed_song,len2=len(subscribed_song))
        elif request.form['submit-button'] == 'remove':
            song_title = request.form.get("title")
            delete_subscription(session['email'],song_title)
            subscribed_song = scan_subscription(session['email'])
            subscribed_song_image = []
            for song in subscribed_song:
                subscribed_song_image.append(create_presigned_url('music-image-assignment2',song['title']))
            return render_template('main.html',user_name=session['user_name'],len=0,subscribed_image=subscribed_song_image,subscribed_song=subscribed_song,len2=len(subscribed_song))
    else:
        if 'login' in session:
            if session['login'] == True:
                subscribed_song = scan_subscription(session['email'])
                subscribed_song_image = []
                for song in subscribed_song:
                    subscribed_song_image.append(create_presigned_url('music-image-assignment2',song['title']))
                return render_template('main.html',user_name=session['user_name'],len=0,len2=len(subscribed_song),subscribed_image=subscribed_song_image,subscribed_song=subscribed_song)
            else:
                return render_template('index.html')
        else:
            return render_template('index.html')

@app.route('/logout',methods=['POST','GET'])
def logout():
    session['login'] = False
    session.pop('user_name',None)
    session.pop('email', None)
    return redirect(url_for("root"))

def query_login(email,password, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('login')
    response = table.query(
        KeyConditionExpression = Key('email').eq(email) & Key('password').eq(password)
    )
    return response['Items']

def query_email(email, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('login')
    response = table.query(
        KeyConditionExpression = Key('email').eq(email)
    )
    print(response['Items'])
    return response['Items']

def add_login(email,password,username, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('login')
    table.put_item(Item={
                'email': email,
                'password': password,
                'user_name': username
            })

def scan_song(title,year,artist, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('music')
    filter_expression_list = []
    if title != "":
        filter_expression_list.append(Attr('title').contains(title))
    if year != "":
        filter_expression_list.append(Attr('year').eq(int(year)))
    if artist != "":
        filter_expression_list.append(Attr('artist').contains(artist))
    filter_expression = None
    first = True
    for filter in filter_expression_list:
        if first:
            filter_expression = filter
            first = False
        else:
            filter_expression = filter_expression & filter
    if filter_expression is not None:
        response = table.scan(
            FilterExpression=filter_expression
            )
        return response['Items']
    else:
        response = table.scan()
        return response['Items']
def subscribe_song(title,artist,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('music')
    response = table.get_item(Key={'title': title, 'artist': artist})
    subscribed_song = response['Item']
    subscription_table = dynamodb.Table('subscription')
    subscription_table.put_item(Item={
                'title': subscribed_song['title'],
                'artist': subscribed_song['artist'],
                'year': subscribed_song['year'],
                'web_url': subscribed_song['web_url'],
                'image_url': subscribed_song['image_url'],
                'email' : session['email']
            })
def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    return response

def scan_subscription(email,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('subscription')
    response = table.scan(
        FilterExpression=Attr('email').eq(email)
    )
    return response['Items']

def delete_subscription(email,title,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table= dynamodb.Table('subscription')
    response = table.delete_item(
        Key={
            'email': email,
            'title': title
        }
    )

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)