from flask import request
from postInfo import app
import boto3
import logging
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime
import json

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_QANDA_TABLE")

'''signUp method will add a record to AWS Cognito and then add those info to User Info Dynamo DB, before
adding to the cognito we will do a check if the email id is already present in the dynamo DB'''


@app.route('/add-qAnda', methods=['POST'])
def addQAndA():
    # logging.log("addAccommodation() request is "+json.dumps(request.get_json()))
    response = {}
    try:
        '''Connect to the User Info table'''
        table = dynamoDbResource.Table(table_name)
        # logging.log("Table is connected")
        item = {"name": request.json['name'],
                "email": request.json['email'],
                "subject": request.json['subject'],
                "addedDateTime":datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "institution": request.json['institution'],
                "description": request.json['description'],
                "answers": request.json['answers']
                }
        '''After adding to the cognito pool add the basic info to user info table'''
        response=table.put_item(Item=item)
        # logging.log("New User added to the Dynamo Db")
    except ClientError as e:
        logging.error(e)
    return response
