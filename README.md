## System Description
This system is a distributed image processing application, allowing the user to upload one or more images, to select the desired operation,
and the system distributes the tasks on multiple VMs to increase the throughput, and then returns the processed images to the user when processing is done.
The system is built on Google Cloud Platform, and uses many technologies, such as Python MPI, and FLASK.

## Once the GUI starts, the user can follow these steps ...
1. The user clicks on the ‘Upload’ button.
2. A file explorer window appears, where the user can select the image(s) desired for processing.
3. The user chooses the image processing operation from a dropdown menu.
4. The user clicks on the ‘Send’ button.
5. The user waits for the processed images
6. After processing is done, the processed images appear on the UI.
7. The user may download the processed images to his device.

## Here's a demo video link, showing the working system ...
https://drive.google.com/drive/folders/1lnm8LqWm3DhVssk8I8n9cVnQQ54lelxL?usp=sharing
