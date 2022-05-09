import json
import time
import urllib.parse
import io
import os
import boto3
from PIL import Image, ImageDraw, ImageFont

print("Loading Function")

#Connect to AWS services
rekog = boto3.client("rekognition")
s3 = boto3.client("s3")
s3Upload = boto3.resource('s3')

def handler(event, context):
	# Get the object from the event and show its content type
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

	try:
		#Get object from s3 bucket put event
		s3response = s3.get_object(Bucket=bucket, Key=key)

		#Pass the object as bytes
		img_bytes = s3response["Body"].read()
		
		#Call detect labels
		response = rekog.detect_labels(Image = {'Bytes': img_bytes}, MaxLabels=1, MinConfidence=70)
		print(response)

		#Get default fonts and text for bounding boxes
		image = Image.open(io.BytesIO(img_bytes))
		font = ImageFont.truetype('/usr/share/fonts/truetype/Arial.ttf', size=48)
		draw = ImageDraw.Draw(image)

		#Get image dimensions
		Width, Height = image.size

		#Get all labels found in image
		for label in response['Labels']:
			name = label['Name']
			conf = label['Confidence']
			lbl = name + " " + str(conf) + "%"

			#Draw all bounding boxes for each label instance
			for instance in label['Instances']:
				
				if 'BoundingBox' in instance:
					boundingBox = instance['BoundingBox']

					#Get bounding box coordinates for the bb instance
					left = int(boundingBox['Left'] * Width)
					top = int(boundingBox['Top'] * Height)
					width = int(boundingBox['Width'] * Width)
					height = int(boundingBox['Height'] * Height)

					#Draw bounding boxes
					draw.rectangle([left, top, width, height], outline=(255,0,0), width=10)
					draw.text((left, height), lbl, font=font, fill=(255, 0, 0))
				else:
					#If there is no bounding boxes, print label only
					draw.text((50*width, 50*height), lbl, font=font, fill=(255, 0, 0))
					
		#Generate new key name for processed picture
		keyOut = time.strftime("%Y%m%d-%H%M%S")+".jpg"
		savePath = f"/tmp/{str(keyOut)}"
		image.save(savePath)

		#Specify destination bucket
		bucketOut = "dics-rekog-output"
		
		#Verify Save
		fileVerify = os.listdir('/tmp')
		print(fileVerify)

		#Upload file to s3 bucket
		s3Upload.meta.client.upload_file(savePath , bucketOut, keyOut)

		#Delete original image uploaded
		s3.delete_object(Bucket=bucket, Key=key)

	except Exception as e:
		print(e)
		print('Error recieving response from AWS.')
		raise e

