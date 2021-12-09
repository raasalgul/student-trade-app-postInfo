import boto3
import logging

from boto3.dynamodb.conditions import Key

from postInfo import application
from flask import request
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import json

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
accommodation_table_name = os.getenv("DYNAMO_ACCOMMODATION_TABLE")
job_table_name = os.getenv("DYNAMO_JOB_TABLE")
oldProducts_table_name = os.getenv("DYNAMO_OLDPRODUCTS_TABLE")
qAndA_table_name = os.getenv("DYNAMO_QANDA_TABLE")
otherServices_table_name = os.getenv("DYNAMO_OTHERSERVICES_TABLE")

bucket_name = os.getenv("S3_BUCKET")

''' Configuring AWS S3 '''
s3 = boto3.resource(os.getenv('AWS_S3'), region_name=os.getenv('AWS_REGION'))

''' getUser() This method get the necessary user information from the user dynamo table. '''


@application.route('/get-postInfo', methods=['POST'])
def getPostInfo():
    response = {}
    try:

        bearer = request.headers.get('Authorization')
        bearer = bearer.replace("Bearer ", "")
        responseUserData = cognitoClient.get_user(AccessToken=bearer)
        logging.info("Response user data {}".format(responseUserData))
        print(responseUserData)
        userEmail = responseUserData['UserAttributes'][3]
        print(userEmail['Value'])
        userEmail = userEmail['Value']
        if responseUserData['ResponseMetadata']['HTTPStatusCode'] == 200:
            ''' Connect with Accommodation Dynamodb table '''
            accommodationTable = dynamoDbResource.Table(accommodation_table_name)

            ''' Connect with Job Table Dynamodb table '''
            jobTable = dynamoDbResource.Table(job_table_name)

            ''' Connect with Old Products Dynamodb table '''
            oldProductsTable = dynamoDbResource.Table(oldProducts_table_name)

            ''' Connect with Q and A Dynamodb table '''
            qAndATable = dynamoDbResource.Table(qAndA_table_name)

            ''' Connect with Other Services Dynamodb table '''
            otherServicesTable = dynamoDbResource.Table(otherServices_table_name)

            logging.log("getUser: Connected to table")
            ''' The key field is used to query the table '''
            key = {"email": request.json['email'],
                   "name":"Flat at dublin 1"
                   }
            ''' Get the entire items from the entire tables '''
            response = {
                "accommodation":accommodationTable.query(
                    KeyConditionExpression = Key("email").eq(request.json['email'])),
                "jobTable":jobTable.query(
                    KeyConditionExpression = Key("email").eq(request.json['email'])),
                "oldProductsTable":oldProductsTable.query(
                    KeyConditionExpression = Key("email").eq(request.json['email'])),
                "qAndATable":qAndATable.query(
                    KeyConditionExpression = Key("email").eq(request.json['email'])),
                "otherServicesTable":otherServicesTable.query(
                    KeyConditionExpression = Key("email").eq(request.json['email']))
            }
            #print("scan "+accommodationTable.scan()['Items'])
            #print("scan " + accommodationTable.scan()['Items'])
            logging.log("getUser: Got response from table {}".format(response))
    except ClientError as e:
        logging.error(e)
    return response
