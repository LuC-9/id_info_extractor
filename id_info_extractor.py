#!/usr/bin/env python
# coding: utf-8

# # ID card Information Extractor

# ## Importing Libraries

# In[1]:


import pytesseract
import cv2
import numpy as np
import sys
import requests
import re
import os
from PIL import Image
import ftfy
import pan_read
import adhar_read
import io
import json
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\KrygO\AppData\Local\Tesseract-OCR\tesseract'


# ## Taking Input from Command Line

# In[10]:


img_url = ""
if len(sys.argv) > 1:
    img_url = "".join(sys.argv[1:])
    print(img_url)
else:
    print("No Input Specified!!!")
    k= input('Press Enter to Exit.')
    exit(1)


# ### Checking the address is URL or path and validity check

# In[11]:


if img_url.startswith('http') or img_url.startswith('www'):
    if not re.match('(?:http|ftp|https)://', img_url):
        img_url =  'http://{}'.format(img_url)
    try:
        r = requests.get(img_url, stream = True)
        if r.headers.get('content-type')[:5] == 'image':
            open('image.jpg','wb').write(r.content)
        else:
            print("Couldn't load image!!")
            k = input("Press Enter to Exit.")
            exit(1)
    except:
        print("Wrong Address!!")
        k= input('Press Enter to Exit.')
        exit(1)
else:
    try:
        img= cv2.imread(img_url)
        cv2.imwrite("image.jpg",img)
    except:
        print("Wrong Address!!")
        k= input('Press Enter to Exit.')
        exit(1)


# ### Checking for clear Image

# In[12]:


img = cv2.imread("image.jpg")
var = cv2.Laplacian(img, cv2.CV_64F).var()
if var < 50:
    print("Image is Too Blurry....")
    k= input('Press Enter to Exit.')
    exit(1)


# ## Extracting Text using PyTesseract

# In[13]:


filename = "image.jpg"
text = pytesseract.image_to_string(Image.open(filename), lang = 'eng')
os.remove(filename)

text_output = open('output.txt', 'w', encoding='utf-8')
text_output.write(text)
text_output.close()

file = open('output.txt', 'r', encoding='utf-8')
text = file.read()

text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)


# ### Check whether PAN or adhaar

# In[14]:


if "income" in text.lower() or "tax" in text.lower() or "department" in text.lower():
    data = pan_read.pan_read_data(text)
elif "male" in text.lower():
    data = adhar_read.adhaar_read_data(text)


# ## Writing for JSON

# In[15]:


try:
    to_unicode = unicode
except NameError:
    to_unicode = str
with io.open('info.json', 'w', encoding='utf-8') as outfile:
    data = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(data))


# ## Reading JSON data

# In[17]:


with open('info.json', encoding = 'utf-8') as data:
    data_loaded = json.load(data)


# In[9]:


if data_loaded['ID Type'] == 'PAN':
    print("\n---------- PAN Details ----------")
    print("\nPAN Number: ",data_loaded['PAN'])
    print("\nName: ",data_loaded['Name'])
    print("\nFather's Name: ",data_loaded['Father Name'])
    print("\nDate Of Birth: ",data_loaded['Date of Birth'])
    print("\n---------------------------------")
elif data_loaded['ID Type'] == 'ADHAAR':
    print("\n---------- ADHAAR Details ----------")
    print("\nADHAAR Number: ",data_loaded['Adhaar Number'])
    print("\nName: ",data_loaded['Name'])
    print("\nDate Of Birth: ",data_loaded['Date of Birth'])
    print("\nSex: ",data_loaded['Sex'])
    print("\n------------------------------------")
k = input("\n\nPress Enter To EXIT")
exit(0)

