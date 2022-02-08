import boto3
import json
from helper import get_param, setup_asana_client, logger

TEMPLATE = "templates/template.md"

asana_client = setup_asana_client()
s3_bucket = get_param('S3BucketDocStore')
s3_client = boto3.client('s3')


def replace_bool_with_str(field):
    new_value = str(asana_fields[field])
    new_value = new_value.replace('True', 'Yes')
    new_value = new_value.replace('False', 'No')
    asana_fields.update({field: new_value})


def replace_num_with_str(field):
    new_value = str(asana_fields[field])
    asana_fields.update({field: new_value})


def replace_empty_with_na(field):
    new_value = "Not Applicable"
    asana_fields[field] = new_value


def flatten_dict(field):
    field_value = asana_fields[field]
    for k, v in field_value.items():
        new_field = field + '_' + k
        asana_fields.update({new_field: v})
    del asana_fields[field]


def replace_list_with_str(field):
    new_value = ""
    for v in asana_fields[field]:
        v = str(v)
        new_value = new_value + v + '\n'
    new_value = new_value.removesuffix('\n')
    asana_fields.update({field: new_value})


def flatten_list_of_dicts(field):
    new_fields = [keys for keys in asana_fields[field][0]]
    for new_field in new_fields:
        new_value = []
        for d in asana_fields[field]:
            try:
                new_value.append(d[new_field])
            except KeyError:
                pass
        new_field = field + '_' + new_field
        asana_fields.update({new_field: new_value})
    del asana_fields[field]


def get_custom_fields():
    logger.info("get the custom_fields from Asansa")
    response = asana_client.tasks.get_task(
        task_id, opt_fields=['custom_fields'], opt_pretty=True)
    return response['custom_fields']


def write_custom_fields_to_asana_fields():
    logger.info("Write the custom_fields to asana_fields")
    for custom_field in custom_fields:
        custom_name = custom_field['name']
        asana_fields.update({custom_name: custom_field})
    logger.info(f"""asana_fields including the custom fields are: \n
                {json.dumps(asana_fields)}""")


def lambda_handler(event, context):

    # Get the task_id by interrogating the event.
    logger.info(f"event is {event}")
    body = json.loads(event['Records'][0]['body'])
    global task_id
    task_id = body['TaskId']
    logger.info(f"task_id is {task_id}")

    # Get the Asana fields
    global asana_fields
    logger.info("get asana_fields")
    asana_fields = asana_client.tasks.get_task(
        task_id, opt_pretty=True)
    logger.info(f"asana_fields are:\n{json.dumps(asana_fields)}")

    # If custom fields present remove and get full custom fields details as
    # separate request. Then write the custom fields to asana_fields.
    if 'custom_fields' in asana_fields:
        asana_fields.pop('custom_fields')
        global custom_fields
        custom_fields = get_custom_fields()
        logger.info(f"custom_fields are:\n{json.dumps(custom_fields)}")
        write_custom_fields_to_asana_fields()
    else:
        logger.info("No custom fields present in response from Asana API")

    logger.info("Start transformation of asana_fields")
    run = True
    run_count = 0
    while run:
        run = False
        for field, value in asana_fields.copy().items():
            if type(value) == bool:
                replace_bool_with_str(field)
            elif type(value) == int or type(value) == float:
                replace_num_with_str(field)
            elif not value:
                replace_empty_with_na(field)
            elif type(value) == dict:
                flatten_dict(field)
                run = True
            elif type(value) == list:
                if type(value[0]) == dict:
                    flatten_list_of_dicts(field)
                    run = True
                else:
                    replace_list_with_str(field)
                run = True
        run_count += 1
        logger.info(
            f"""The asana_fields after transformation run {run_count} is:
            \n{json.dumps(asana_fields)}""")
    logger.info("Completed transformation of asana_fields")
    logger.info(f"Complete list of fields is:\n {list(asana_fields)}")

    logger.info(f"Get template markdown file {TEMPLATE} and extract text")
    input_file = open(TEMPLATE, 'r')
    input_text = input_file.read()
    output_text = input_text
    logger.info(f"Extracted text from {TEMPLATE}")

    logger.info("""Searching markdown template for placeholders that match
    field. Replace if match found.""")
    for k, v in asana_fields.items():
        placeholder = "{" + k + "}"
        if input_text.find(placeholder) != -1 and v:
            output_text = output_text.replace(placeholder, v)
        else:
            logger.debug(
                f"""placeholder {placeholder} not in markdown template or value
                 is empty""")
    logger.info("Finished replacing placeholders.")

    logger.info("Write new markdown text to file.")
    output_file = open('/tmp/AsanaTask.md', 'w')
    output_file.write(output_text)
    output_file.close()
    logger.info("Written new markdown text to file.")

    logger.info("Upload markdown file to S3 bucket")
    s3_client.upload_file('/tmp/AsanaTask.md', s3_bucket,
                          f"{task_id}/AsanaTask.md")
    logger.info("Uploaded markdown file to S3 bucket")
