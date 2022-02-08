import boto3
import os
from helper import get_param, setup_asana_client, logger

asana_client = setup_asana_client()

# Setup S3 Client
s3_bucket = get_param('S3BucketDocStore')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    # Grab the Asana Task ID from the S3 object path.
    logger.info("Get task_id")
    s3_object_key = event['Records'][0]['s3']['object']['key']
    task_id = s3_object_key.split("/")[0]
    logger.info(f"The task_id is {task_id}")

    # Download the PDF file from the S3 bucket.
    logger.info("Download the PDF file.")
    response = s3_client.download_file(
        s3_bucket, f"{task_id}/AsanaTask.pdf", "/tmp/AsanaTask.pdf")
    logger.info(f"The response from the s3_client is {response}")

    # Get and remove existing attachment(s) created by this application.
    attachments = asana_client.attachments.get_attachments_for_task(
        task_id, opt_pretty=True)
    logger.info(f"Existing attachments are {attachments}")
    for attachment in attachments:
        attachment_name = attachment['name']
        if attachment_name == f"asana_task_{task_id}":
            logger.info(
                f"attachment_name is {attachment_name}. Created by this application: deleting.")
            attachment_id = attachment['gid']
            response = asana_client.attachments.delete_attachment(
                attachment_id, opt_pretty=True)
            logger.info(
                f"The response from  the delete attachment request is {response}.")
        else:
            logger.info(f"""
            attachment_name is {attachment_name}.
            Not created by this application so ignoring.""")

    # Upload PDF file to Asana
    logger.info("Upload pdf file to Asana")
    with open("/tmp/AsanaTask.pdf", "rb") as task_file:
        task_data = task_file.read()
    response = asana_client.attachments.create_attachment_for_task(
        task_id, file_content=task_data, file_name=f"asana_task_{task_id}",
        file_content_type="application/pdf")
    logger.info(
        f"The response for the create attachment request is {response}")
    os.remove("/tmp/AsanaTask.pdf")
