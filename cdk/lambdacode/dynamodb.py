import os
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dev-dataeng-meetup-table')

print(table.creation_date_time)
def main(event, context):
    print(event)

    data = json.load(event)
    print(data)
    # print(i)
    # table.put_item(
    #     Item=i
    # )
