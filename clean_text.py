# %% Imports 

import os
import sys
import getopt
import re
import json
from datetime import datetime
from time import tzname
import time
import pandas as pd
import glob
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import nltk

# nltk.download('words')
english_words = set(nltk.corpus.words.words())

def remove_extra_spaces(content, rep):

    for i in range(rep):
        words = content.split()

        cleaned_words = []
        for i in range(len(words)):
            if i > 0 and words[i-1][-1].isalpha() and words[i][0].isalpha() and (words[i-1]+words[i]).lower() in english_words:
                cleaned_words.pop()
                cleaned_words.append(words[i-1]+words[i])
            else:
                cleaned_words.append(words[i])

        content = " ".join(cleaned_words)
    
    return content
    

# %% Files with resolutions, clean documents
df_info = pd.read_csv("iris_documents_pdf.csv", index_col=False)
df_resolutions = pd.DataFrame()

names = df_info['number'].to_list()
titles = df_info['title'].to_list()
names = [".".join(name.split("/")) for name in names]

start_phrase = ["Seventy-third", "Seventy-fourth", "Seventy-fifth"]
pattern = r"WHA\d+\.\d+\.txt"  # \d+ matches one or more digits
uppercase_pattern = r'(?<!\S)[A-Z\s]+\b'

for year in range(1948, 2023):
    print(year)
    folder_path = f"text_documents/{year}"
    files = []
    for filename in os.listdir(folder_path):
        if re.match(pattern, filename):
            files.append(f"text_documents/{year}/{filename}")

    if len(files)==0:
        files = glob.glob(f"text_documents/{year}/WHA*.resolutions.txt")
        
    if not os.path.exists(f"cleaned_text_documents/{year}"):
        os.makedirs(f"cleaned_text_documents/{year}")

    for file in files:
        if os.path.exists(f"cleaned_text_documents/{year}/"+file.split("/")[-1]):
            continue

        with open(file) as f:
            text = f.readlines()

        text = "".join(text)
        text = text.replace("\n", "")
        text = text.replace("  ", " ")
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        # removing references of type "text,43 " to "text "
        text = re.sub(r',\d+\s', ' ', text)
        
        text = " ".join([word for word in text.split() if 'http' not in word])

        if not re.match(pattern, file.split('/')[-1]):
            print(file)
            start_line = f"The {start_phrase[year-2020]} World Health Assembly, "
            wha_text = file.split("/")[-1].split(".")[0]
            res_num = 1
            st = 0
            while 1:
                wha_num = f"{wha_text}.{res_num}"
                match = re.search(r'{}'.format(re.escape(wha_num)), text)
                if match:
                    if res_num>1:
                        res_text = text[st:match.start()]
                        match_ss = re.search(r'{}'.format(re.escape(start_line)), res_text)
                        res_title = " ".join(res_text[:match_ss.start()].split()[1:])
                        if res_title.split()[-1].isdigit():
                            if len(res_title.split()[-1]) % 2 == 1:
                                res_title = " ".join(res_title.split()[:-1]+[res_title.split()[-1][:-1]])
                        else:
                            if res_title.split()[-1][-1].isdigit():
                                res_title = " ".join(res_title.split()[:-1]+[res_title.split()[-1][:-1]])
                        res_title = res_title.split()
                        for j in range(len(res_title)):
                            if res_title[j].isdigit() and len(res_title[j]) == 8:
                                res_title[j] = res_title[j][:4] + "-" + res_title[j][4:]
                        res_title = " ".join(res_title)
                        res_id = res_text[:match_ss.start()].split()[0]
                        print(res_title)
                        row = pd.DataFrame([{'number': res_id, 'title': res_title}])
                        df_resolutions = pd.concat([df_resolutions, row])
                        with open(f"cleaned_text_documents/{year}/"+f"{wha_text}.{res_num-1}"+".txt", "w") as f:
                            t2w = res_text[match_ss.end():]
                            t2w = t2w.split()
                            t2w_final = ""
                            for j in range(len(t2w)):
                                if j==0:
                                    t2w_final = t2w[j]
                                elif t2w[j][0]=="-":
                                    t2w_final = t2w_final+t2w[j]
                                else:
                                    t2w_final = t2w_final+" "+t2w[j]
                            f.write(t2w_final)
                    res_num = res_num + 1
                    st = match.start()
                else:
                    res_text = text[st:]
                    match_ss = re.search(r'{}'.format(re.escape(start_line)), res_text)
                    res_title = " ".join(res_text[:match_ss.start()].split()[1:])
                    if res_title.split()[-1].isdigit():
                        if len(res_title.split()[-1]) % 2 == 1:
                            res_title = " ".join(res_title.split()[:-1]+[res_title.split()[-1][:-1]])
                    else:
                        if res_title.split()[-1][-1].isdigit():
                            res_title = " ".join(res_title.split()[:-1]+[res_title.split()[-1][:-1]])
                    res_title = res_title.split()
                    for j in range(len(res_title)):
                        if res_title[j].isdigit() and len(res_title[j]) == 8:
                            res_title[j] = res_title[j][:4] + "-" + res_title[j][4:]
                    res_title = " ".join(res_title)
                    res_id = res_text[:match_ss.start()].split()[0]
                    print(res_title)
                    row = pd.DataFrame([{'number': res_id, 'title': res_title}])
                    df_resolutions = pd.concat([df_resolutions, row])
                    with open(f"cleaned_text_documents/{year}/"+f"{wha_text}.{res_num-1}"+".txt", "w") as f:
                        t2w = res_text[match_ss.end():]
                        t2w = t2w.split()
                        t2w_final = ""
                        for j in range(len(t2w)):
                            if j==0:
                                t2w_final = t2w[j]
                            elif t2w[j][0]=="-":
                                t2w_final = t2w_final+t2w[j]
                            else:
                                t2w_final = t2w_final+" "+t2w[j]
                        f.write(t2w_final)
                    break
            continue

        x = ".".join(file.split("/")[-1].split(".")[:-1])
        I = names.index(x)

        row = pd.DataFrame([{'number': x, 'title': titles[I]}])
        df_resolutions = pd.concat([df_resolutions, row])
        # print(f"\n{x}: {titles[I]}")

        substring = titles[I].lower().replace("\n", "")
        substring = re.sub(r'[^\x00-\x7F]+', '', substring)
        larger_string = text
        L = len(substring)

        # Initialize variables for best match and its score
        best_match = ""
        best_score = 0
        best_start = 0
        best_end = 0

        matches, scores, starts, ends = [], [], [], []
        for i in range(len(larger_string) - L):
            window = larger_string[i:i+L]
            try:
                match, score = process.extractOne(substring, [window], scorer=fuzz.token_set_ratio, score_cutoff=80)
            except:
                continue
            
            matches.append(match)
            scores.append(score)
            starts.append(i)
            ends.append(i + len(window))
        if len(scores)>0:
            J = np.argmax(scores)
            best_match = matches[J]
            best_score = scores[J]
            best_start = starts[J]
            best_end = ends[J]

            header = text[:best_start]
            content = text[best_end:].strip()
        else:
            header = ""
            content = text
        content = content.replace("/"," / ")

        cleaned_content = remove_extra_spaces(content, 2)
        # print(cleaned_content)

        with open(f"cleaned_text_documents/{year}/"+file.split("/")[-1], "w") as f:
            t2w = cleaned_content
            t2w = t2w.split()
            t2w_final = ""
            for j in range(len(t2w)):
                if j==0:
                    t2w_final = t2w[j]
                elif t2w[j][0]=="-":
                    t2w_final = t2w_final+t2w[j]
                else:
                    t2w_final = t2w_final+" "+t2w[j]
            f.write(t2w_final)
            # f.write(cleaned_content)

    df_resolutions.to_csv("wha_resolutions.csv", index=False)

df_resolutions.to_csv("wha_resolutions.csv", index=False)

# ocrmypdf.ocr(f'{files[0]}', 'output.pdf', deskew=True, force_ocr=True)  

# %%
