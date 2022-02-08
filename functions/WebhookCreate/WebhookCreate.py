import secrets
import botocore.exceptions
from helper import get_param, put_param, setup_asana_client, logger

asana_client = setup_asana_client()

# Define Asana variables
workspace_id = get_param('WorkspaceId')
logger.info(f"workspace_id is {workspace_id}")
project_id = get_param('ProjectId')
logger.info(f"project_id is {project_id}")


def lambda_handler(event, context):
    logger.info(f"Event is:\n{event}")

    # Generate a token ('url_token') to append as a query string
    logger.info("Generating secret to use for url_token")
    url_token = secrets.token_urlsafe(64)
    logger.info("Secret generated")
    put_param('URLToken', url_token, 'SecureString')
    logger.info("Secret stored as 'URLToken' parameter")

    # Combine the API URL with the url_token generated to generate target_url
    logger.info("Generating target_url using url_token for query string.")
    api_url = get_param('APIURL')
    target_url = api_url + "?" + 'url_token' + '=' + url_token
    logger.info("target_url generated")

    try:
        old_webhook_id = get_param('WebhookId')
        logger.info(f"The current stored webhook id is {old_webhook_id}")
        logger.info(f"Deleting existing web hook with Id: {old_webhook_id}")
        asana_response = asana_client.webhooks.delete_webhook(
            old_webhook_id, opt_pretty=True)
        logger.info(f"Response to delete webhook request is {asana_response}")
    except botocore.exceptions.ClientError:
        logger.info("Cannot delete existing webhook or no webhook to delete")

    # Formulate Asana request to create webhook
    asana_request = {
        "filters": [
          {
            "action": "changed",
            "resource_type": "task",
          }
        ],
        "resource": project_id,
        "target": target_url
      }
    logger.info("The Asana request to create the webhook has been generated.")

    # Setup flag to true to allow the receive function to establish the webhook
    response = put_param('Setup', 'True', 'SecureString')
    logger.info(f"Setup flag set as parameter. Response is {response}.")

    # Create the webhook
    asana_response = asana_client.webhooks.create_webhook(
        asana_request, opt_pretty=True)
    new_webhook_id = asana_response['gid']
    put_param('WebhookId', new_webhook_id, 'String')
    logger.info(
        f"New webhook with Id {new_webhook_id} created and parameter stored")
