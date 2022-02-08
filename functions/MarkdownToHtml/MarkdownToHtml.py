import boto3
import os
import mistletoe
from helper import get_param, logger


def lambda_handler(event, context):

    logger.info(f"event is {event}")

    # Grab the Asana Task ID from the S3 object path.
    s3_object_key = event['Records'][0]['s3']['object']['key']
    task_id = s3_object_key.split("/")[0]

    # Setup S3 Client
    s3_bucket = get_param('S3BucketDocStore')
    s3_client = boto3.client('s3')

    # Download the markdown file from the S3 bucket.
    s3_client.download_file(
        s3_bucket, f'{task_id}/AsanaTask.md', '/tmp/AsanaTask.md')

    with open("/tmp/AsanaTask.md", "r") as input_file:
        input_text = input_file.read()
    os.remove('/tmp/AsanaTask.md')

    output_text = mistletoe.markdown(input_text)

    output_file = open('/tmp/AsanaTask.html', 'w')
    output_file.write(output_text)
    output_file.close()
    response = s3_client.upload_file(
        '/tmp/AsanaTask.html', s3_bucket, f'{task_id}/AsanaTask.html')
    logger.info(f"Response to s3 upload file request is: {response}")
    os.remove('/tmp/AsanaTask.html')
