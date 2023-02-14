from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict as predict_pb2
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

# Load the dataset
df = pd.read_csv("dataset.csv")

# Select the features for clustering
X = df[["first_name", "last_name", "email", "gender", "ip_address"]]

# Preprocess the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Set the number of clusters
num_clusters = 3

# Set the container image URI for the GMM model
container_image_uri = "us-docker.pkg.dev/vertex-ai/prediction/gaussian-mixture-model:latest"

# Create the model container specification
model_container_spec = {
    "image_uri": container_image_uri,
}

# Create the GMM model
model = aiplatform.Model(
    display_name="gmm-clustering-model",
    container_spec=model_container_spec,
    predict_schemata=predict_pb2.ValueSpec(
        encoded_value=predict_pb2.EncodedValueSpec(
            tensor_shape=predict_pb2.TensorShape(dim=[predict_pb2.FixedDim(size=5)])
        )
    ),
)

# Create the input data configuration
input_data_config = {
    "instances": [
        {
            "first_name": x[0],
            "last_name": x[1],
            "email": x[2],
            "gender": x[3],
            "ip_address": x[4],
        }
        for x in X_scaled
    ]
}

# Set the number of clusters in the explanation metadata
explanation_metadata = {
    "inputs": {
        "first_name": {"type": "CATEGORY"},
        "last_name": {"type": "CATEGORY"},
        "email": {"type": "CATEGORY"},
        "gender": {"type": "CATEGORY"},
        "ip_address": {"type": "CATEGORY"},
    },
    "outputs": {"cluster": {"type": "CATEGORY", "number_of_categories": num_clusters}},
}

# Set the explanation spec
explanation_spec = {"metadata": explanation_metadata}

# Train the GMM model and deploy it to an endpoint
endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=1,
)

# Create a prediction request for a sample dataset
sample_dataset = [
    {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "gender": "Female", "ip_address": "123.45.67.89"},
    {"first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "gender": "Male", "ip_address": "98.76.54.32"},
    {"first_name": "Charlie", "last_name": "Lee", "email": "charlie@example.com", "gender": "Male", "ip_address": "12.34.56.78"},
]
sample_dataset_scaled = scaler.transform(pd.DataFrame(sample_dataset)[["first_name", "last_name", "email", "gender", "ip_address"]])
prediction_request = predict_pb2.PredictRequest(
    instances=[{"values": [list(row)]} for row in sample_dataset_scaled],
    parameters={"explanation_spec": explanation_spec},
)

# Make the prediction request using the Vertex AI Python SDK
response = endpoint.predict(prediction_request)

# Get the cluster assignments from

# Extract the predicted clusters
predicted_clusters = np.array(response.predictions[0].tables.values).flatten()

# Print the predicted clusters for each sample dataset
for i, cluster in enumerate(predicted_clusters):
    print(f"Sample dataset {i+1} is assigned to cluster {cluster}")
