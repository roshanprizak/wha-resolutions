# A closer look into the resolutions of the World Health Assembly
Dataset of WHA resolutions, NLP analysis of topics and time evolution, network analysis of WHA resolutions, and examining countries' scale of assessments.

Read about this project [here](https://roshanprizak.com/projects/health/wha_resolutions/analyze_keywords.html).

# Pipeline

## Data download

First `run scrape_iris.py` to download the PDF files of the resolutions of the World Health Assembly from the [IRIS website](https://apps.who.int/iris/) into the directory `data/IRIS_documents/`. This also stores the year, associated ID and the title of each document. Of these documents, the ones which actually are WHA resolutions or contain WHA resolutions are of interest to us. For most years, each resolution is contained in its own independent PDF file with a filename like WHA34.7.pdf, where 34 is the session number and 7 is the resolution number. This WHA34.7 also acts as the associated ID for the resolution. However, for 2020, 2021 and 2022, the resolutions are all contained in a single PDF file with many other documents. After downloading all the files, one has to manyally remove the extra pages from the documents for 2020-22 and rename the files as WHA75.resolutions.pdf or similar, where 75 is the session number.

## PDF to text

To convert the PDF files to text, run `make_text.py`. This uses PyPDF2 to extract text from the PDF files. The text files are stored with the same filename as the PDF file but with a .txt extension. The files are stored in `data/text_documents/`.

## Cleaning the text

To clean the text files, remove headers, unwanted special characters, and extract individual resolutions from the combined files for 2020-22, run `clean_text.py`. This stores the cleaned text files in `data/cleaned_text_documents/`. There should be one file per resolution. The titles of these resolutions are stored in `data/wha_resolutions.csv`.

## NLP and network analysis

Use the Jupyter notebook `analyze_keywords.ipynb` to perform further analysis. Any networks generated as part of the analysis are stored as GraphML files and can be visualized/analyzed with Gephi, for exmaple. 

## Scale of assessments

The resolutions containing information about the scale of assessments were extracted using a semi-automated pipeline as in `analyze_scale_of_assessments.ipynb`. I obtained one file per decade as I had to also convert these PDFs to clean numbers with some manual juggling.
