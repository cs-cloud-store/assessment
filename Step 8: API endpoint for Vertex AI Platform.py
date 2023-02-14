from googleapiclient import discovery
from google.oauth2 import service_account
import numpy as np

# Specify the project ID and the name of the model to be deployed
PROJECT_ID = 'hale-brook-377621'
MODEL_NAME = 'your-model-name'

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file('path/to/your/credentials.json')

# Create a client object for the AI Platform Prediction service
ml = discovery.build('ml', 'v1', credentials=credentials)

# Define a function to preprocess the input data before making predictions
def preprocess(input_data):
    # Apply any necessary preprocessing steps here, such as scaling or one-hot encoding
    return input_data

# Define a function to make predictions using the deployed model
def predict(input_data):
    # Preprocess the input data
    preprocessed_data = preprocess(input_data)

    # Create a request body for the prediction request
    request_body = {"instances": preprocessed_data.tolist()}

    # Make the prediction request using the AI Platform Prediction API
    parent = f'projects/{PROJECT_ID}/models/{MODEL_NAME}'
    response = ml.projects().predict(name=parent, body=request_body).execute()

    # Extract the predicted labels from the response
    predicted_labels = np.array(response['predictions']).flatten()

    # Return the predicted labels
    return predicted_labels

#gcloud command to run on Cloud shell
gcloud ai-platform models create your-model-name --regions=us-central1
gcloud ai-platform versions create your-version-name --model=your-model-name --runtime-version=2.5 --python-version=3.7 --framework=scikit-learn --origin=gs://your-bucket/path/to/model --project=hale-brook-377621
