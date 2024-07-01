import os
import boto3
from PIL import Image
import io

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    try:
        # Check if 'Records' exist in the event
        if 'Records' in event and len(event['Records']) > 0:
            # Process the first record assuming it's an S3 event
            record = event['Records'][0]
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']

            # Download the image from S3
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            image_content = response['Body'].read()

            # Check if image is already 400x400
            if is_image_already_resized(image_content):
                return {
                    'statusCode': 200,
                    'body': f"Image is already resized to 400x400: {object_key}"
                }

            # Resize the image
            resized_image_content = resize_image(image_content)

            # Upload the resized image back to S3
            resized_key = object_key.split('.')[0] + "_resized." + object_key.split('.')[1] if '.' in object_key else object_key + "_resized"
            s3_client.put_object(Bucket=bucket_name, Key=resized_key, Body=resized_image_content, ContentType='image/png')

            return {
                'statusCode': 200,
                'body': f"Resized image saved to {resized_key}"
            }
        else:
            return {
                'statusCode': 400,
                'body': "No valid S3 records found in the event"
            }
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': f"KeyError: {e}"
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Unexpected error: {e}"
        }


def resize_image(image_content):
    with io.BytesIO(image_content) as image_file:
        with Image.open(image_file) as image:
            image = image.resize((400, 400))
            with io.BytesIO() as output:
                image.save(output, format="PNG")
                return output.getvalue()


def is_image_already_resized(image_content):
    with io.BytesIO(image_content) as image_file:
        with Image.open(image_file) as image:
            return image.size == (400, 400)