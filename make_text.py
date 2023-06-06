# %% Imports 

import os
import sys
import getopt
import re
from urllib.request import urlopen
import json
from datetime import datetime
from time import tzname
import time
import requests
from urllib.parse import urlparse
import pandas as pd
import glob
from PyPDF2 import PdfReader

# %% Files with resolutions

pattern = r"WHA\d+\.\d+\.pdf"  # \d+ matches one or more digits

for year in range(1948, 2023):
    print(year)
    folder_path = f"data/IRIS_documents/{year}"
    files = []
    for filename in os.listdir(folder_path):
        if re.match(pattern, filename):
            files.append(f"data/IRIS_documents/{year}/{filename}")

    if len(files)==0:
        files = glob.glob(f"data/IRIS_documents/{year}/WHA*.resolutions.pdf")

    if not os.path.exists(f"data/text_documents/{year}"):
        os.makedirs(f"data/text_documents/{year}")
        
    for file in files:
        reader = PdfReader(file)
        if len(reader.pages)==0:
            print(f"{year}: {file}")
        text = ""
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            
            page_text = page.extract_text()
            page_text = page_text.replace("-\n", "")
            text = text + page_text

        with open(f"data/text_documents/{year}/"+".".join(file.split("/")[-1].split(".")[:-1])+".txt", "w") as f:
            f.write(text)

# %%
