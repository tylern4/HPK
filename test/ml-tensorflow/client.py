from __future__ import print_function

import base64
import io
import json

import numpy as np
from PIL import Image
import requests

RESNET_IP = '128.55.71.95'

# The server URL specifies the endpoint of your server running the ResNet
# model with the name "resnet" and using the predict interface.
SERVER_URL = 'http://128.55.81.13:8501/v1/models/resnet:predict'

# The image URL is the location of the image we should send to the server
IMAGE_PATH = 'dog.jpg'

# Path to the ImageNet classes file
IMAGENET_CLASSES_PATH = 'imagenet_classes.txt'

# Current Resnet model in TF Model Garden (as of 7/2021) does not accept JPEG
# as input
MODEL_ACCEPT_JPG = False

def load_imagenet_classes():
    """Load ImageNet class names from the file."""
    with open(IMAGENET_CLASSES_PATH, 'r') as f:
        return [line.strip() for line in f.readlines()]

def main():
    # Load the ImageNet class names
    class_names = load_imagenet_classes()

    # Download the image
    with open(IMAGE_PATH, 'rb') as image_file:
        image_data = image_file.read()

    # Compose a JSON Predict request (send the image tensor).
    jpeg_rgb = Image.open(io.BytesIO(image_data))
    # Normalize and batchify the image
    jpeg_rgb = np.expand_dims(np.array(jpeg_rgb) / 255.0, 0).tolist()
    predict_request = json.dumps({'instances': jpeg_rgb})

    # Compose a JSON Predict request (send JPEG image in base64).
    jpeg_bytes = base64.b64encode(image_data).decode('utf-8')
    predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

    # Send few requests to warm-up the model.
    for _ in range(1):
        response = requests.post(SERVER_URL, data=predict_request)
        response.raise_for_status()

    # Send few actual requests and report average latency.
    total_time = 0
    num_requests = 1
    predictions = []
    for _ in range(num_requests):
        response = requests.post(SERVER_URL, data=predict_request)
        response.raise_for_status()
	 # Print the whole response
        print("Full Response JSON:", response.json())
        total_time += response.elapsed.total_seconds()
        prediction = response.json()['predictions'][0]['probabilities']
        predictions.append(prediction)

    # Print average latency
    # print("Class predicted: ", np.argmax(prediction))
    # print("All predictions: ", prediction)
    # Find the index of the highest probability
    max_index = prediction.index(max(prediction))

    print(f"The index of the highest probability is: {max_index}")
    print(f"The highest probability is : {max(prediction)}")
    print(f"The length of probabilities is: {len(prediction)}")
    avg_latency = (total_time * 1000) / num_requests
    print(f'Average latency: {avg_latency:.2f} ms')


if __name__ == '__main__':
    main()
