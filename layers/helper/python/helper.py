import asana
import boto3
import os
import logging

parameter_path = os.environ['ParameterPath']

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info(f"Logger configured: {logger}")


def setup_asana_client():
    # Create Asana Client
    logger.info("Retrieving Asana Token")
    asana_token = get_param('AsanaToken')
    logger.info("The Asana token is "
                + asana_token.replace(asana_token, "[Token obscured for security]"))
    return asana.Client.access_token(asana_token)


def get_param(name):
    ssm_client = boto3.client('ssm')
    param = ssm_client.get_parameter(
        Name=parameter_path+name, WithDecryption=True)
    param = param['Parameter']['Value']
    return param


def put_param(name, value, type):
    ssm_client = boto3.client('ssm')
    response = ssm_client.put_parameter(Name=parameter_path+name, Value=value,
                                        Type=type, Overwrite=True)
    return response
