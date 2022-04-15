# MoexAPI

I have chosen **MoexApi** for my test project and made it in script form. (script was possible assuming my dialog with HR)

## Requirements and Set Up

Requirements consist of **requests** mostly, other dependencies are sub-dependencies.

To start script we need to make virtual environment, activate it and install requirements 
(optionally, only **requests** dependency is needed, probably you already have it)

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Now we can start process:

    python main.py


## Purpose
Idea of script is to get exact security detail info answering on questions. 
Prints and inputs are dummies instead of frontend, it was done to make ability to interact with client
and have different variants as the result.

### Why script?
I could choose Django to build this client, but it's pretty overhead for 4 external api requests. 
FastApi or AioHttp would be better option as more lightweight solution, but I don't have experience with them for now.

### Problems
I faced one problem during test. I expected good-working API with JSON type. Reality was different, JSON was awful, 
and could ask too much iteration:

    "columns": ["TRADEDATE", "SECID", "SHORTNAME", "BOARDID",.....], 
    "data": [["2022-04-14", "AFKS", "Система ао", "SOTC",]
             ["2022-04-14", "AGRO", "AGRO-гдр", "SOTC",...],

I continue working on it because I said, that I choose MOEX. 
That is why I decided to use XML format and learn how to parse it in process. 
If it's a problem I can make another project with proper API.

### Time
A spent 6 hours to make it, navigating in MOEX docs took too much time (about 3), 
not all endpoints were available without subscribe. So it was hard to make logical and interesting path of requests. 
1 hours spent on XML parsing theory, and 2 hours to write and refactor code. Approximate timings.
