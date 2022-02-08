<link rel="stylesheet" href="markdown.css">

# Asana-AWS-TaskDoc

Example markdown template.
Edit / extra / reuse as required.
Any text inside the braces '{}' are placeholders and will be replaced by the
value of the Asana field when the workflow runs.

### Example Table

| Field                         | Value              |
|-------------------------------|--------------------|
| **Reference**                 | {gid}              |
| **Project Reference(s)**      | {projects_gid}     |
| **Project Name(s)**           | {projects_name}    |
| **Assignee**                  | {assignee_name}    |
| **Task Title**                | {name}             |
| **Completion Status**         | {completed}        |
| **Estimated Completion Date** | {due_on}           |

'gid' is the global identifier that provides a unique reference number for
all Asana resources.

### Title

The field name for the title of the task is name.

### Description

The field name for the description of the task is notes.

### List of Supported Standard Fields

The placeholders for the standard fields follow. When the application is run against the template and task, the placeholders will be replaced with the actual values from the corresponding Asana field. The fields have been flattenned, For example, assignee_section_resource_type is the resource_type sub-field, within the section subfield, within the assignee field.

{gid}
{assignee_status}
{completed}
{completed_at}
{created_at}
{due_at}
{due_on}
{hearted}
{hearts}
{liked}
{likes}
{modified_at}
{name}
{notes}
{num_hearts}
{num_likes}
{parent}
{permalink_url}
{resource_type}
{start_at}
{start_on}
{resource_subtype}
{assignee_gid}
{assignee_name}
{assignee_resource_type}
{assignee_section_gid}
{assignee_section_name}
{assignee_section_resource_type}
{followers_gid}
{followers_name}
{followers_resource_type}
{memberships_project_gid}
{memberships_project_name}
{memberships_project_resource_type}
{memberships_section_gid}
{memberships_section_name}
{memberships_section_resource_type}
{projects_gid}
{projects_name}
{projects_resource_type}
{tags_gid}
{tags_name}
{tags_resource_type}
{workspace_gid}
{workspace_name}
{workspace_resource_type}


### Custom Fields ###

Custom fields are supported. The placeholder to use depends on the field type and name.
Most of the fields that Asana generates will not be of much use in a document.
The main one to use is:

{MyCustomFieldName_display_value}

This will give the same value as is shown in the Asana web app.
MyCustomFieldName should be replaced by the actual field name as is
shown in the Asana web app.

For a text field, the fields will use this format:

{MyCustomFieldName_created_by_gid}
{MyCustomFieldName_created_by_name}
{MyCustomFieldName_created_by_resource_type}
{MyCustomFieldName_display_value}
{MyCustomFieldName_enabled}
{MyCustomFieldName_gid}
{MyCustomFieldName_name}
{MyCustomFieldName_resource_subtype}
{MyCustomFieldName_resource_type}
{MyCustomFieldName_text_value}
{MyCustomFieldName_type}

For single-select fields, the format will be:

{MyCustomFieldName_created_by_gid}
{MyCustomFieldName_created_by_name}
{MyCustomFieldName_created_by_resource_type}
{MyCustomFieldName_display_value}
{MyCustomFieldName_enabled}
{MyCustomFieldName_enum_options_color}
{MyCustomFieldName_enum_options_enabled}
{MyCustomFieldName_enum_options_gid}
{MyCustomFieldName_enum_options_name}
{MyCustomFieldName_enum_options_resource_type}
{MyCustomFieldName_enum_value_color}
{MyCustomFieldName_enum_value_enabled}
{MyCustomFieldName_enum_value_gid}
{MyCustomFieldName_enum_value_name}
{MyCustomFieldName_enum_value_resource_type}
{MyCustomFieldName_gid}
{MyCustomFieldName_name}
{MyCustomFieldName_resource_subtype}
{MyCustomFieldName_resource_type}
{MyCustomFieldName_type}

For number fields, the format will be:

{MyCustomFieldName_created_by_gid}
{MyCustomFieldName_created_by_name}
{MyCustomFieldName_created_by_resource_type}
{MyCustomFieldName_display_value}
{MyCustomFieldName_enabled}
{MyCustomFieldName_gid}
{MyCustomFieldName_name}
{MyCustomFieldName_number_value}
{MyCustomFieldName_precision}
{MyCustomFieldName_resource_subtype}
{MyCustomFieldName_resource_type}
{MyCustomFieldName_type}
