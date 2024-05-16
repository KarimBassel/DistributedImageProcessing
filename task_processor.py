from mpi4py import MPI
import json
import math
import os
import cv2
from google.cloud import storage  # Optional for Google Cloud Storage
import io
import numpy as np
import base64
project_id = "distcomp-4eng"

def encode2_image_to_base64(image_array):
  # Convert the NumPy array to a PIL Image object (assuming RGB or grayscale)
  from PIL import Image
  if len(image_array.shape) == 2:
    image = Image.fromarray(image_array, mode='L')  # Grayscale mode
  else:
    # Handle potential channel order issues (BGR vs RGB)
    if image_array.shape[-1] == 3 and image_array.dtype == np.uint8:
      # Assuming uint8 and potential BGR order, convert to RGB
      image = Image.fromarray(image_array[:, :, ::-1], mode='RGB')
    else:
      image = Image.fromarray(image_array, mode='RGB')  # Default to RGB mode
  # Create a BytesIO object to store the image data in memory
  with io.BytesIO() as output:
    image.save(output, format='jpeg')
    contents = output.getvalue()
  mime_type = 'image/jpeg'
  # Encode the image data to base64 string
  encoded_data =  base64.b64encode(contents).decode('utf-8')
  return f"data:{mime_type};base64,{encoded_data}"

def encode_image_to_base64(filename):
  with open(filename, 'rb') as f:
    image_data = f.read()
    print(image_data)
    mime_type = 'image/jpeg'  # Replace with appropriate format based on filename extension
    encoded_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_data}"

def decode_image(image_data):
  # Split the data into parts
  header, data = image_data.split(',')
  mime_type, encoding = header.split(';')
  if encoding == 'base64':
    # Decode the base64 encoded data
    decoded_data = base64.b64decode(data)
  # Create a BytesIO object to store the decoded data
  image_buffer = io.BytesIO(decoded_data)
  # Import the appropriate image library based on mimetype
  if mime_type == 'data:image/jpeg':
    from PIL import Image
    # Load the image from the BytesIO object
    img = Image.open(image_buffer)
    return img
  elif mime_type == 'data:image/png':
    from PIL import Image
    # Load the image from the BytesIO object
    img = Image.open(image_buffer)
    return img

def image_to_json_string2(image):
  # Convert image data to a list (assuming uint8 format)
  image_data = image.flatten().tolist()
  encoded_string = json.dumps(image_data)
  return encoded_string

def image_to_json_string(image_path):
  with open(image_path, "rb") as image_file:
      image_data = list(image_file.read())  # Convert to list for JSON
      encoded_string = json.dumps(image_data)
      return encoded_string

# Function to send task and image data to a worker
def send_task_to_worker(worker_rank, task):
  task_json = json.dumps(task)
  comm.send(task_json.encode(), dest=worker_rank)

#Function implemented in the slave nodes
def process_image(task):
  # Extract image path and operation from the task dictionary
  operation = task[0]
  # Load the image in a numpy array to apply operation
  img = decode_image(image_data=task[1])
  img = np.array(img)
  # Perform the specified image processing operation
  if operation == "grayscale":
    result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  elif operation == "edge_detection":
    result = cv2.Canny(img, 100, 200)
  elif operation == "color_inversion":
    result = cv2.bitwise_not(img)
  elif operation == "blur":
    result = cv2.blur(img, (5,5))
  elif operation == "image_segmentation":
    thresh, result = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
  
  return result

# MPI initialization
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


# Master node behavior (rank 0)
if rank == 0:
  data_list = []
  task=[]
  with open("ops.txt", 'r') as f:
      for line in f:
        line = line.strip()
        data_list.append(line)
        if(len(data_list)==2):
          task.append(data_list)
          data_list =[]

  ops = len(task)-1
  #Load Balancing of Tasks between slaves
  slave1 = math.ceil((ops+1)/2)
  slave2 = math.floor((ops+1)/2)
  # Distribute tasks to worker nodes
  send_task_to_worker(1, task[0:slave1])
  if slave2>0 : send_task_to_worker(2, task[slave1:slave1+slave2])
  #gather results from slave nodes
  res=1
  filename = "res.txt"
  with open(filename ,'w') as outfile: 
    for opsslave1 in range(0,slave1):
      buffer_size = 10000000
      data_type = MPI.CHAR
      results = comm.recv(buf=bytearray(buffer_size), source=1)
      results = json.loads(results.decode())
      outfile.write(results + '\n')
      print(results)
      results = decode_image(image_data=results)
      #Define the image path and filename
      image_path = "/home/karimbassel15/result" +str(res) + ".jpeg"
      res+=1
      #Save the image as JPEG format
      results.save(image_path, format="JPEG")
      print(f"Image saved successfully: {image_path}")
      print(results)

    for opsslave2 in range(0,slave2):
      buffer_size = 10000000
      data_type = MPI.CHAR
      results = comm.recv(buf=bytearray(buffer_size), source=2)
      results = json.loads(results.decode())
      outfile.write(results + '\n')
      print(results)
      results = decode_image(image_data=results)
      #Define the image path and filename
      image_path = "/home/karimbassel15/result" +str(res) + ".jpeg"
      res+=1
      #Save the image as JPEG format
      results.save(image_path, format="JPEG")
      print(f"Image saved successfully: {image_path}")
      print(results)

# Worker node behavior (rank > 0)
else:
  # Receive task data from master
  buffer_size = 10000000
  data_type = MPI.CHAR
  task_json = comm.recv(buf=bytearray(buffer_size), source=0)
  task = json.loads(task_json.decode())
 # Process the task on the received image
  for i in range(0,len(task)):
    result = process_image(task[i])
    resultstr = encode2_image_to_base64(result)
    task_json = json.dumps(resultstr)
    comm.send(task_json.encode() , dest=0)

# Finalize MPI
MPI.Finalize()
