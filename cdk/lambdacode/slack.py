import os
import json
import requests
import boto3
from botocore.exceptions import ClientError


secret_name = "secrets_automating_slack_signups"
region_name = "ap-southeast-2"

session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
)

try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
        print("The requested secret " + secret_name + " was not found")
    elif e.response['Error']['Code'] == 'InvalidRequestException':
        print("The request was invalid due to:", e)
    elif e.response['Error']['Code'] == 'InvalidParameterException':
        print("The request had invalid params:", e)
else:
    # Secrets Manager decrypts the secret value using the associated KMS CMK
    # Depending on whether the secret was a string or binary, only one of these fields will be populated
    if 'SecretString' in get_secret_value_response:
        text_secret_data = get_secret_value_response['SecretString']
    else:
        binary_secret_data = get_secret_value_response['SecretBinary']

slack_webhook_url = json.loads(text_secret_data)['slack_webhook_url']

webhook_url = slack_webhook_url
postChannel = "testing"
postIcon = ":mailbox_with_mail:"
postUser = "Form Response"
postColor = "#0000DD"
messageFallback = "The attachment must be viewed as plain text."
messagePretext = "A user submitted a response to the form."

def main(event, context):
    print(event)

    try:
        submit_result = submitValuesToSlack(event)
        print(submit_result)
    except Exception as e:
        print('There was an error!')
        print('Caught this error: ' + repr(e))

    return event



def submitValuesToSlack(e):
    attachments = constructAttachments(e['values'])

    payload = {
        "channel": postChannel,
        "username": postUser,
        "icon_emoji": postIcon,
        "link_names": 1,
        "attachments": attachments
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(payload))
        print(response)
    except Exception as e:
        print('There was an error!')
        print('Caught this error: ' + repr(e))


# // Creates Slack message attachments which contain the data from the Google Form
# // submission, which is passed in as a parameter
# // https://api.slack.com/docs/message-attachments
def constructAttachments(values):
    fields = makeFields(values)

    attachments = [{
        "fallback" : messageFallback,
        "pretext" : messagePretext,
        "mrkdwn_in" : ["pretext"],
        "color" : postColor,
        "fields" : fields
    }]

    return attachments

# // Creates an array of Slack fields containing the questions and answers
def makeFields(values):
    print(values)
    fields = []

    columnNames = ['timestamp','email','first_name','last_name']

    for num, col in enumerate(columnNames):
        print(f'num: {num}, col: {col}')
        colName = col
        val = values[num]
        fields.append(makeField(colName, val))

    return fields

# // Creates a Slack field for your message
# // https://api.slack.com/docs/message-attachments#fields
def makeField(question, answer):
    field = {
        "title" : question,
        "value" : answer,
        "short" : False
    }
    return field


