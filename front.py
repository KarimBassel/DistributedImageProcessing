import tkinter as tk
import json
import base64
import cv
import io
import PIL
import time
import pickle
from tkinter import filedialog,Frame,Label,scrolledtext
import requests  # For API calls

# FLASK API URL
API_URL = "http://130.211.77.184:8000/process_image"

def select_image():
  global image_path, selected_operations
  image_path = []
  filenames = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
  if filenames:
    st = ""
    for filename in filenames:
      image_path.append(filename)
      st += filename + ","
      print(image_path)
    variable.set(st)

def choose_operation():
  global selected_operation
  selected_operation = operation_var.get()

def encode_image_to_base64(image_data):
  mime_type = 'image/jpeg'  # Replace with appropriate format based on filename extension
  encoded_data = base64.b64encode(image_data).decode('utf-8')
  #print(len(encoded_data))
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

def send_to_api():
  inittime = time.time()
  if not image_path:
    return
  data ={}
  print(image_path)
  # Open image in binary mode
  for i in range(0,len(image_path)):
    with open(image_path[i], "rb") as image_file:
      image_data = image_file.read()
    tempdic = {"im"+str(i):encode_image_to_base64(image_data)}
    data.update(tempdic)
  count_label.config(text="Image Count = " + str(len(image_path)))

  dic = {'operation' : operation_var.get()}
  data.update(dic)
  json_data = json.dumps(data)
  # Send POST request with multipart form data
  response = requests.post(API_URL,data=json_data)
  responsetime = time.time()
  time_label.config(text=f"{responsetime - inittime} s")
  print(response)
  cntr=0
  if response.status_code == 200:
    print(len(response.json()))
    imlist=[]
    for i in range(0,len(response.json())):
      image = response.json().get("res"+str(i))
      imlist.append(image)
      # Label to display response from API
      label_response = tk.Label(root, text="")
      cntr+=1
      if(cntr==6):
        label_response.pack(side="top")
        cntr=0
      else : label_response.pack(side="left")

      from PIL import ImageTk
      image = decode_image(image)
      photo_image = ImageTk.PhotoImage(image)
      #Add image to label
      label_response.config(image=photo_image)
      label_response.image = photo_image
    image_label.config(text=f"Status : SUCCESS")
  else:
    image_label.config(text=f"Error: {response.status_code}")

# Create the main window
root = tk.Tk()
root.title("Image Processing App")

# Label for response image count
count_label = tk.Label(root, text="")
count_label.pack()


# Label for response time
time_label = tk.Label(root, text="")
time_label.pack()

# Label for image selection
label_image = tk.Label(root, text="Select Image:")
label_image.pack()

# Button to open file dialog
button_select = tk.Button(root, text="Browse", command=select_image)
button_select.pack()

# Create a label for response status
image_label = tk.Label(root)
image_label.pack()



# Label to display selected image filename
variable = tk.StringVar()
label_filename = tk.Label(root, textvariable=variable)
label_filename.pack()

# Dropdown menu for operation selection
operation_var = tk.StringVar()
operation_var.set("Select Operation")  # Default value
operations = ["grayscale", "color_inversion", "edge_detection" ,"blur","image_segmentation"]
operation_menu = tk.OptionMenu(root, operation_var, *operations)
operation_menu.pack()

# Button to send data to API
button_send = tk.Button(root, text="Send to API", command=send_to_api)
button_send.pack()

# Label to display response from API
label_response = tk.Label(root, text="")
label_response.pack()


# Global variables to store image path and selected operation
image_path = None
selected_operation = None

# Run the main loop
root.mainloop()
