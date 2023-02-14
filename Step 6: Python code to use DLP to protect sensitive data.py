import google.cloud.dlp
from google.cloud import dlp_v2

# Instantiates a DLP client
dlp = dlp_v2.DlpServiceClient()

# Define the info types to be de-identified
info_types = [{"name": "PERSON_NAME"}, {"name": "EMAIL_ADDRESS"}, {"name": "IP_ADDRESS"}]

# Define the de-identification transformation
deidentify_config = {
    "record_transformations": {
        "field_transformations": [
            {
                "fields": [{"name": "first_name"}, {"name": "last_name"}, {"name": "email"}],
                "primitive_transformation": {
                    "character_mask_config": {
                        "masking_character": "*",
                        "number_to_mask": 0.6,
                        "characters_to_ignore": [{"characters_to_skip": ".,;:-'\"()"}],
                    }
                },
            },
            {
                "fields": [{"name": "ip_address"}],
                "primitive_transformation": {
                    "replace_with_info_type_config": {"info_type": {"name": "IP_ADDRESS"}},
                },
            },
        ]
    },
    "info_type_transformations": {"transformations": [{"info_types": info_types, "action": {"redact": {}}}]},
}

# Define the re-identification transformation
reidentify_config = {
    "record_transformations": {
        "field_transformations": [
            {
                "fields": [{"name": "first_name"}, {"name": "last_name"}, {"name": "email"}],
                "primitive_transformation": {"replace_with_info_type_config": {"info_type": {"name": "PERSON_NAME"}}},
            },
            {"fields": [{"name": "ip_address"}], "primitive_transformation": {"replace_with_info_type_config": {"info_type": {"name": "IP_ADDRESS"}}}},
        ]
    },
    "info_type_transformations": {"transformations": [{"info_types": info_types, "action": {"replaceWithInfoTypeConfig": {"infoType": {"name": "PII"}}}}]},
}

# Define the dataset
dataset = [
    {"id": 1, "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "gender": "male", "ip_address": "192.168.0.1"},
    {"id": 2, "first_name": "Jane", "last_name": "Doe", "email": "jane.doe@example.com", "gender": "female", "ip_address": "192.168.0.2"},
]

# De-identify the dataset
deidentify_request = dlp_v2.DeidentifyContentRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
    deidentify_config=deidentify_config,
    item={"table": {"headers": [{"name": "id"}, {"name": "first_name"}, {"name": "last_name"}, {"name": "email"}, {"name": "gender"}, {"name": "ip_address"}], "rows": [{"values": [str(d[key]) for key in ["id", "first_name", "last_name", "email", "gender", "ip_address"]]} for d in dataset]}},
)
deidentified_response = dlp.deidentify_content(deidentify_request)
deidentified_dataset = [{header["name"]: row["values"][i] for i, header in enumerate(deidentified_response.item.table.headers)} for row in deidentified_response.item.table.rows]

# Re-identify the dataset
reidentify_request = dlp_v2.ReidentifyContentRequest(
parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
reidentify_config=reidentify_config,
inspect_config={"info_types": info_types},
item={"table": {"headers": [{"name": "id"}, {"name": "first_name"}, {"name": "last_name"}, {"name": "email"}, {"name": "gender"}, {"name": "ip_address"}], "rows": [{"values": [str(d[key]) for key in ["id", "first_name", "last_name", "email", "gender", "ip_address"]]} for d in deidentified_dataset]}},
)
reidentified_response = dlp.reidentify_content(reidentify_request)
reidentified_dataset = [{header["name"]: row["values"][i] for i, header in enumerate(reidentified_response.item.table.headers)} for row in reidentified_response.item.table.rows]

#Print the original and re-identified datasets to test the code
print("Original dataset:")
print(dataset)
print("Re-identified dataset:")
print(reidentified_dataset)
css

