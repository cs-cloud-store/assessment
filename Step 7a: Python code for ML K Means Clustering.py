from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from google.cloud.aiplatform_v1.types import (
    DeployedModel,
    ExplanationMetadata,
    ExplanationParameters,
    ExplanationSpec,
    InputDataConfig,
    Model,
    ModelContainerSpec,
    Port,
    PredictRequest,
    PredictionInput,
    PredictionOutput,
)
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

# Set the project and location
PROJECT_ID = "hale-brook-377621"
LOCATION = "us-central1"

# Set the name and location of the dataset file
DATASET_PATH = "gs://your-bucket/dataset.csv"

# Create a Vertex AI client
client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
client = aiplatform.gapic.JobServiceClient(client_options=client_options)

# Load the dataset
df = pd.read_csv(DATASET_PATH)

# Select features for clustering
X = df[["first_name", "last_name", "email", "gender", "ip_address"]]

# Preprocess the features using standard scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Set the number of clusters
num_clusters = 3

# Set the container image URI
image_uri = "us-docker.pkg.dev/vertex-ai/prediction/kmeans-cpu.1-0:latest"

# Create the model container specification
model_container_spec = ModelContainerSpec(image_uri=image_uri)

# Create the K-Means model
model = Model(
    display_name="kmeans-model",
    container_spec=model_container_spec,
    metadata_schema_uri="gs://google-cloud-aiplatform/schema/prediction/classification_1.0.0.yaml",
)

# Create the input data configuration
input_data_config = InputDataConfig(
    instances_format="json",
    json_instance_schema_uri="gs://google-cloud-aiplatform/schema/prediction/input/text_classification_example.json",
)

# Create the explanation spec
explanation_metadata = ExplanationMetadata(
    inputs={"features": {"input_tensor_name": "input"}}
)
explanation_parameters = ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 20}}
)
explanation_spec = ExplanationSpec(
    metadata=explanation_metadata, parameters=explanation_parameters
)

# Create the model deployment
deployed_model = DeployedModel(model=model)
endpoint = aiplatform.Endpoint.create(
    display_name="kmeans-endpoint", explanation_spec=explanation_spec
)
endpoint.deploy(
    deployed_model=deployed_model,
    traffic_percentage=100,
    machine_type="n1-standard-2",
)

# Create a prediction request for a sample dataset
input_data = [{"first_name": row[0], "last_name": row[1], "email": row[2], "gender": row[3], "ip_address": row[4]} for row in X.values]
predict_request = PredictRequest(
    endpoint=endpoint.resource_name,
    instances=[json_format.Parse(json_format.MessageToJson(PredictionInput(data=InputDataConfig.EncodedData(json_format.Parse(json_format.MessageToJson(Value(json_value=bytes(json.dumps(instance), "utf-8"))))))), PredictRequest) for instance in input_data],
)

# Make a prediction request
response = client.predict(predict_request)

# Get the cluster assignments
cluster_assignments = np.array([np.argmax(prediction.outputs["scores"].value) for prediction in response.predictions])

#add a new column in the dataset
df["cluster"] = cluster_assignments
#Print the dataset with the predicted clusters
print(df.head())
