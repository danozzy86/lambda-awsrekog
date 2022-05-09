# lambda-awsrekog
Lambda funtion that uses S3ObjectPut trigger to collect uploaded image from S3 bucket an run it through AWS Rekognition. Once it recieves the response from AWS Rekognition, it attempts to draw bounding boxes over the detected labels if coordinates are present in the response. The image is drawn on using Pillow, saved, and then uploaded to a seperate S3 bucket. Once the image is uploaded to the new bucket, they original image is deleted from the source S3 bucket.

This Lambda function is contained in a docker image and can not run natively on AWS Lambda
