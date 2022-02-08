import hashlib
import hmac
import json
import boto3
from helper import get_param, put_param, logger


def lambda_handler(event, context):
    logger.info("Getting url_token_expected and url_token_received")
    url_token_received = event['queryStringParameters']['url_token']
    url_token_expected = get_param('URLToken')
    logger.info("url_token_expected matches url_token_received")
    if url_token_received == url_token_expected:
        if 'X-Hook-Secret' in event['headers']:
            x_hook_secret = event['headers']['X-Hook-Secret']
            logger.info(
                "New X-Hook-Secret received. Checking to see if new webhook setup allowed.")
            setup = get_param('Setup')
            if setup == 'True':
                logger.info(
                    """New X Hook Secret received and setup is allowed,
                     so webhook will be configured.""")
                logger.info("Writing X Hook Secret to parameter store")
                put_param('XHookSecret', x_hook_secret, 'SecureString')
                logger.info("Written X Hook Secret back to parameter store")
                logger.info("Setting the setup parameter to 'false'")
                setup = put_param('Setup', 'False', 'SecureString')
                logger.info("The setup parameter has been set to 'False'")
                logger.info("Returning X Hook Secret back to Asana")
                return {"statusCode": "200",
                        "headers": {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'X-Hook-Secret': x_hook_secret
                                    }
                        }
            else:
                logger.error("Setup flag not set, so no setup allowed")
                raise ValueError("Setup flag not set, so no setup allowed")
        else:
            logger.info(
                "No X-Hook-Secret received. Assume using existing webhook.")
            if "X-Hook-Signature" in event["headers"]:
                logger.info("""X-Hook-Signature present. Use X Hook Secret to
                    generate signature and compare.""")
                x_hook_secret = get_param('XHookSecret')
                signature = hmac.new(bytes(x_hook_secret, 'utf-8'), msg=bytes(
                    event['body'], 'utf-8'), digestmod=hashlib.sha256).hexdigest()
                if signature == event["headers"]["X-Hook-Signature"]:
                    logger.info(
                        "Signatures match. Obtain Task ID that has changed")
                    body = json.loads(event['body'])
                    logger.info(f"The body of the response is {body}")
                    if body['events'][0]['resource']['gid']:
                        logger.info(
                            "Task Id is present in body. Gettting Task Id ")
                        task_id = body['events'][0]['resource']['gid']
                        task_json = json.dumps({'TaskId': task_id})
                        logger.info(
                            f"Task Id is {task_id}. Placing Task in queue.")
                        queue_url = get_param('SQSQueueTask')
                        sqs = boto3.resource('sqs')
                        logger.info(f"queue_url is {queue_url}")
                        queue = sqs.Queue(queue_url)
                        response = queue.send_message(MessageBody=task_json)
                        logger.info(
                            f"Response from send message call is {response}")
                        logger.info(
                            "Returning Status Code 200 back back to Asana")
                        return {"statusCode": "200",
                                "headers": {
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                            }
                                }
                    elif body:
                        logger.error(
                            "No Task Id in body but body not empty. Malformed body.")
                        raise ValueError(
                            "No Task Id in body but body not empty. Malformed body.")
                    else:
                        logger.info("Body is empty: Heartbeat event")
                        logger.info(
                            "Returning Status Code 200 back back to Asana")
                        return {"statusCode": "200",
                                "headers": {
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                            }
                                }
                else:
                    logger.error("Signatures do not match.")
                    raise ValueError("Signatures do not match.")
            else:
                logger.error("No signature received.")
                raise ValueError("No signature received.")
    else:
        logger.error(
            "url_token_expected does not match url_token_received or URL is malformed.")
        raise ValueError(
            "url_token_expected does not match url_token_received or URL is malformed.")
