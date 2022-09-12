import requests
import boto3
import os

def lambda_handler(event, context):
    username = 'xxxxxxx';
    password= 'xxxxxxx';
    clientId= 'xxxxxxx';
    region = 'us-east-1';
    arn = os.environ['SNS_TOPIC_ARN'];
    bearer_token = get_accessToken(username, password, clientId, region);
    data = getAllRDS(bearer_token, region);
    count = getCount(data);
    if (count > 15):
        sendEmail(arn);
        return 'Limit surpassed';
    else:
        return 'Limit NO surpassed';
    
    
def get_accessToken(username, password, clientId, region='us-east-1'):

    client = boto3.client('cognito-idp', region_name=region);
    response = client.initiate_auth(
        ClientId=clientId,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    );
    id_token = response['AuthenticationResult']['IdToken'];
    bearer_token = 'Bearer '+ id_token;

    return bearer_token

def getAllRDS(bearer_token, region='us-east-1'):
    Headers={'Authorization': bearer_token};
    r = requests.get(f'https://api.cursocloudaws.net/oteador/services/AllInstancesRDS/region/{region}', headers=Headers);
    data = r.json();
    return data;

def getCount(data):
    try:
        count = len(data[0]['Id']);
    except IndexError:
        count = 0;
    return count;
    
def sendEmail(arn):
    client = boto3.client('sns')
    snsArn = arn
    message = "The EC2 instance limit has been surpassed."
    
    response = client.publish(
        TopicArn = snsArn,
        Message = message ,
        Subject='Alert'
    )