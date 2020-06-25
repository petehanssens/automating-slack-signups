import os
from mailchimp3 import MailChimp
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

user = json.loads(text_secret_data)['mailchimp_user']
api_key = json.loads(text_secret_data)['mailchimp_api_key']
audience_id = json.loads(text_secret_data)['mailchimp_audience_id']

client = MailChimp(mc_api=api_key, mc_user=user)


def main(event, context):
    print(event)
    email = event['namedValues']['Email Address'][0]
    first_name = event['namedValues']['first_name'][0]
    last_name = event['namedValues']['last_name'][0]
    print(f'{first_name} {last_name} has signed up using their email: {email}')

    try:
        # add John Doe with email john.doe@example.com to list matching id '123456'
        response = client.lists.members.create(audience_id, {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': first_name,
                'LNAME': last_name,
            },
        })

        print(response)
    except Exception as e:
        print('There was an error!')
        print('Caught this error: ' + repr(e))

    return event
