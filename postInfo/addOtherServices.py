from flask import request
from postInfo import application
import boto3
import logging
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import json

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_OTHERSERVICES_TABLE")
hashTable_name = os.getenv("DYNAMO_HASH_TABLE")

bucket_name = os.getenv("S3_BUCKET")

''' Configuring AWS S3 '''
s3 = boto3.resource(os.getenv('AWS_S3'), region_name=os.getenv('AWS_REGION'))

'''signUp method will add a record to AWS Cognito and then add those info to User Info Dynamo DB, before
adding to the cognito we will do a check if the email id is already present in the dynamo DB'''


@application.route('/add-other-services', methods=['POST'])
def addOtherProducts():
    logging.info("addAccommodation() request is "+json.dumps(request.get_json()))
    response = {}
    try:
        '''Connect to the User Info table'''
        table = dynamoDbResource.Table(table_name)
        logging.info("Table is connected")

        bearer = request.headers.get('Authorization')
        bearer = bearer.replace("Bearer ", "")
        responseUserData = cognitoClient.get_user(AccessToken=bearer)
        logging.info("Response user data {}".format(responseUserData))
        print(responseUserData)
        userEmail = responseUserData['UserAttributes'][3]
        print(userEmail['Value'])
        userEmail = userEmail['Value']
        if responseUserData['ResponseMetadata']['HTTPStatusCode'] == 200:
            addedDateTime=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            uploadedFile = request.files['file']
            s3_key = userEmail + '/profile-picture-' + addedDateTime + "-" + uploadedFile.filename
            '''We will be forming a folder like structure in S3 where profile-picture will be the folder and 
            the file name will start with Id (email Id) concatenate with current time followed by the uploaded file name'''
            response = s3.meta.client.upload_fileobj(uploadedFile, bucket_name, s3_key,
                                                     ExtraArgs={"ACL": "public-read"})
            logging.info('Uploaded the picture to S3 {}'.format(response))
            s3Url = "{0}.s3.amazonaws.com/{1}".format(bucket_name, s3_key)
            s3Url = "https://" + s3Url.replace(" ", "+").replace(":", "%3A")
            print('Uploaded the picture to S3 {}'.format(s3Url))

            req = request.form['data']
            req = json.loads(req)

            item = {"name": req['name'],
                    "email": req['email'],
                    "addedDateTime":addedDateTime,
                    "institution": req['institution'],
                    "description": req['description'],
                    "picture": s3Url,
                    "price":req['price'],
                    "comments":req['comments']
                    }
            strToHash = item.get("name") + item.get("email") + item.get("addedDateTime")
            hash = hashlib.sha224(strToHash.encode())
            item['hash']=hash.hexdigest()
            response=table.put_item(Item=item)

            hashTable=dynamoDbResource.Table(hashTable_name)
            hashItem={
                "name": req['name'],
                "email": req['email'],
                "hash":hash.hexdigest(),
                "addedDateTime":addedDateTime
            }
            hashTableResponse=hashTable.put_item(Item=hashItem)
            logging.info("New User added to the Dynamo Db")
    except ClientError as e:
        logging.error(e)
    return response
