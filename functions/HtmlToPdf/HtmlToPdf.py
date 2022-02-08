import os
import boto3
import shutil
from helper import get_param, logger


# Setup S3 Client
s3_bucket = get_param('S3BucketDocStore')
logger.info(f"s3_bucket is {s3_bucket}")
logger.info("Create s3_client")
s3_client = boto3.client('s3')
logger.info("s3_client created. Response is {response}")

CSS_FILE = "markdown.css"
CSS_DIR = "css"


def lambda_handler(event, context):

    # Grab the Asana Task ID from the S3 object path.
    logger.info(f"event is {event}")
    s3_object_key = event['Records'][0]['s3']['object']['key']
    task_id = s3_object_key.split("/")[0]
    logger.info(f"task_id is {task_id}")

    # Download the HTML file from the S3 bucket
    logger.info("Download HTML file.")
    response = s3_client.download_file(
        s3_bucket, f"{task_id}/AsanaTask.html", "/tmp/AsanaTask.html")
    logger.info(f"Downloaded HTML file. Response is {response}")

    # Copy css file out of the code package and place in tmp directory to use with html file.
    shutil.copy2(f'{CSS_DIR}/{CSS_FILE}', f'/tmp/{CSS_FILE}')

    # Run the wkhtmltopdf command to convert the HTML file to a PDF file.
    os.system(
        "wkhtmltopdf --enable-local-file-access /tmp/AsanaTask.html /tmp/AsanaTask.pdf")

    # Upload to S3
    response = s3_client.upload_file(
        '/tmp/AsanaTask.pdf', s3_bucket, f"{task_id}/AsanaTask.pdf")
    logger.info("Removing temp files from OS")
    os.remove("/tmp/AsanaTask.html")
    os.remove("/tmp/AsanaTask.pdf")
    logger.info("Files removed.")
