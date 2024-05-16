import subprocess
from flask import Flask, request, jsonify,json,send_file
import io
import time
from PIL import Image
import numpy as np
import cv2
import base64
import os  # for file operations

def encode_image_to_base64(filename):
  with open(filename, 'rb') as f:
    image_data = f.read()
    mime_type = 'image/jpeg'
    encoded_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_data}"

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
  #data sent in the body of the http request from the UI
  datadic = json.loads(request.data)
  operation = datadic['operation']
  #write tasks in a text file
  filename="ops.txt"
  with open(filename, 'w') as outfile:
    for i in range(0,int((len(datadic)-1))):
      task = []
      task.append(operation)
      task.append(datadic["im"+str(i)])
      outfile.write('\n'.join(task) + '\n')
      print(f"Image and operation data saved to: {filename}")

  import subprocess
  #mpiexec command
  mpiexec_cmd = f"mpiexec -n 3 --oversubscribe python3 /home/karimbassel15/task_processor.py -H 130.211.77.184 35.228.104.118 104.198.11.105"
  subprocess.Popen(mpiexec_cmd.split())
  #wait for results to be ready
  if(len(datadic)>30):delay=15
  else : delay = 2
  time.sleep(delay)
  #fault tolerance(resend request if any fault happened)
  filename="res.txt"
  with open(filename, 'r') as f:
    lines = f.readlines()
    if(len(lines) != (len(datadic)-1)):
      mpiexec_cmd = f"mpiexec -n 3 --oversubscribe " \
                    f"python3 /home/karimbassel15/task_processor.py -H 130.211.77.184 35.228.104.118 104.198.11.105"
      subprocess.Popen(mpiexec_cmd.split())
      #wait for results to be ready
      if(len(datadic)>30):delay=15
      else : delay = 2
      time.sleep(delay)

  #read results
  resdic ={}
  cnt=0
  with open(filename , 'r') as f:
    for line in f:
       tempdic = {"res"+str(cnt) : line}
       resdic.update(tempdic)
       cnt+=1
       tempdic={}
  print(resdic)
  return jsonify(resdic)
if __name__ == '__main__':
  app.run(debug=False,port=8000)
  CORS(app)
