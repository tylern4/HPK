"""A client that performs inferences on a ResNet model using the REST API.

The client downloads a test image of a cat, queries the server over the REST API
with the test image repeatedly and measures how long it takes to respond.

The client expects a TensorFlow Serving ModelServer running a ResNet SavedModel
from:

https://github.com/tensorflow/models/tree/master/official/vision/image_classification/resnet#pretrained-models

Typical usage example:

    resnet_client.py
"""

from __future__ import print_function

import base64
import io
import json

import numpy as np
from PIL import Image
import requests



RESNET_IP = '128.55.70.208'

# The server URL specifies the endpoint of your server running the ResNet
# model with the name "resnet" and using the predict interface.
SERVER_URL = 'http://128.55.73.142:8501/v1/models/resnet:predict'

# The image URL is the location of the image we should send to the server
IMAGE_PATH = 'dog.jpg'

# Current Resnet model in TF Model Garden (as of 7/2021) does not accept JPEG
# as input
MODEL_ACCEPT_JPG = False


def main():
  # Download the image
  
  with open(IMAGE_PATH, 'rb') as image_file:
        image_data = image_file.read()

  
    # Compose a JOSN Predict request (send the image tensor).
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
    total_time += response.elapsed.total_seconds()
    prediction = response.json()['predictions'][0]
    predictions.append(prediction)

  # Print the first three predictions
  for i, prediction in enumerate(predictions[:3], start=1):
      print(f'Prediction {i}: {prediction}')

    # Print average latency
  avg_latency = (total_time * 1000) / num_requests
  print(f'Average latency: {avg_latency:.2f} ms')


if __name__ == '__main__':
  main()
