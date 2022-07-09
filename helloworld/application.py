#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import boto3
from flask_cors import CORS
import random



application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}}) 


@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)




#Get Predictions (DynamoDB)
@application.route('/getPredictions', methods=['GET'])
def getPredictions():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('predictions')
    response = table.scan()

    return Response(json.dumps(response['Items']), mimetype='application/json', status=200)    
# curl http://localhost:8000/getPredictions



# Save Prediction (DynamoDB)
@application.route('/addPrediction', methods=['POST'])
def addPrediction():
    data = request.data
    data_json = json.loads(data)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('predictions')
    prediction_id = (str(round(random.uniform(1, 10000000000000))))
    data_json['prediction_id'] = prediction_id
    table.put_item(Item=data_json)
    
    return Response(json.dumps({'Output': 'Succeed'}), mimetype='application/json', status=200)
# curl -i -X POST -H "Content-Type: application/json" -d '{"user_id": "1"}' http://localhost:8000/addPrediction






# Upload Image File to S3 and Save Target URL to DynamoDB
@application.route('/uploadImage', methods=['POST'])
def uploadImage():
    bucket = 'cloud-management-project-jce'
    #image_file = request.files['image_file']
    #image_id = (str(round(random.uniform(1, 10000000000000))))
    
    s3 = boto3.resource('s3', region_name='us-east-1')
    image_path = "7464511074.jpg"
    #image_path  = "%s.jpg" %  image_id
    #s3.Bucket(bucket).upload_fileobj(image_file, image_path, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}) 
    url = 'https://cloud-management-project-jce.s3.amazonaws.com/'+ image_path
    
    
    rekognition = boto3.client("rekognition", region_name = 'us-east-1')
    

    response = rekognition.detect_text(
    Image={
        'S3Object': {
            'Bucket': bucket,
            'Name': image_path,
        }
    }
    )
    
    text_detected = response['TextDetections'][0]['DetectedText']
    confidence = response['TextDetections'][0]['Confidence']

    return {"url": url, "text_detected":text_detected, "confidence":confidence }


if __name__ == '__main__':
    flaskrun(application)

