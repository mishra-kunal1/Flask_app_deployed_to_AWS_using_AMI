from botocore.exceptions import ClientError

import json
import boto3


def handler(event, context):
    username = json.loads(event['Records'][0]['Sns']['Message'])['Username']
    token = json.loads(event['Records'][0]['Sns']['Message'])['Subject']
    subject = json.loads(event['Records'][0]['Sns']['Message'])['Message_type']
    send_email(username, token, subject)


def send_email(email, token, subject):

    SENDER = "studentaccountverification@mishrakunal.me"

    RECIPIENT = email

    authlink = "https://mishrakunal.me/verify?email=" + email + "&token=" + token

    print(authlink)

    DESTINATION = {
        'ToAddresses': [
            RECIPIENT,
        ]
    }

    AWS_REGION = "us-east-1"

    SUBJECT = subject+" for Student's account subscription for final demo"

    BODY_TEXT = ("Email verification for new student\r\n"
                 "Details:\r\n"
                 "\n"
                 "Name: " + email + "\n"
                 "\n"
                 "Verifying email id: " + email + "\r\n"
                 "\r\n"
                 "Use the link provided below to verify yourself to get portal access:\r\n"
                 "Verify: " + authlink
                 )

    CHARSET = "UTF-8"

    client = boto3.client('ses')

    try:
        response = client.send_email(
            Destination=DESTINATION,
            Message={
                'Body': {

                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        print(RECIPIENT)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
