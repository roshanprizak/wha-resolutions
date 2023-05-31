# %% imports 

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
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

if not os.path.exists("IRIS_documents"):
    os.makedirs("IRIS_documents")

# %% make list of documents with links to their HTML pages

df_info = pd.DataFrame()
start_session = 1
end_session = 75
n_repeat = 2

documents_added = []
for session in range(start_session, end_session+1):
    print(session)
    for i in range(1, n_repeat+1):
        page = 1
        while 1:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            url = f"https://apps.who.int/iris/discover?page={page}&filtertype_0=author&filtertype_1=subject&filtertype_2=iso&filter_relational_operator_1=equals&filter_relational_operator_0=equals&filter_2=en&filter_1=Resolutions+and+decisions&filter_relational_operator_2=equals&filter_0=World+Health+Assembly%2C+{session}"
            artifacts = soup.find_all("div", class_="artifact-description") 
            if len(artifacts)>0:
                page = page + 1
            else:
                break

            for artifact in artifacts:
                X = artifact.find("h4", class_="artifact-title")
                title = X.get_text().strip()
                link = "https://apps.who.int" + X.find("a")["href"]

                try:
                    document_number = artifact.find("span", class_="govdoc").get_text().strip()
                except:
                    document_number = "-"

                date = artifact.find("span", class_="date").get_text().strip()

                row = pd.DataFrame([{'number': document_number, 'date': date, 'title': title, 'url': link}])
                if document_number!="-" and document_number not in documents_added:
                    documents_added.append(document_number)
                    df_info = pd.concat([df_info, row])
                elif document_number=="-":
                    df_info = pd.concat([df_info, row])

        df_info.to_csv("iris_documents.csv", index=False)

df_info.to_csv("iris_documents.csv", index=False)

# %% visit each HTML page and add pdf link

df_info = pd.read_csv("iris_documents.csv", index_col=False)
df_info['pdf'] = ""
for i in range(len(df_info)):
    print(f"{i}/{len(df_info)}")
    response = requests.get(df_info['url'][i])
    soup = BeautifulSoup(response.content, "html.parser")
    pdf_links = []
    for link in soup.find_all("a"):
        try:
            if ".pdf" in link["href"]:
                pdf_links.append(link["href"])
        except:
            continue
    df_info['pdf'][i] = pdf_links[-1]

    df_info.to_csv("iris_documents_pdf.csv", index=False)

df_info.to_csv("iris_documents_pdf.csv", index=False)

# %% download each documents

df_info = pd.read_csv("iris_documents_pdf.csv", index_col=False)
for i in range(len(df_info)):
    print(f"{i}/{len(df_info)}")
    if not os.path.exists(f"IRIS_documents/{df_info['date'][i]}"):
        os.makedirs(f"IRIS_documents/{df_info['date'][i]}")

    filename = ".".join(df_info['number'][i].split("/"))
    if filename=="-":
        filename = df_info['pdf'][i].split("?")[0].split("/")[-1].split(".")[0]

    response = requests.get("https://apps.who.int"+df_info['pdf'][i])
    with open(f"IRIS_documents/{df_info['date'][i]}/{filename}.pdf", 'wb') as f:
        f.write(response.content)
# %%
