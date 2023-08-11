### About the Summarization API

This repo consist of pyhton scripts which uses openai chatCompletion api for Text Summarization

**Below are the steps to setup and run the code**

## 1. clone the repo

create folder where you want to keep the project
clone the repo
open git bash inside that folder and run command

```bash
git clone <repo-url> ./
```

## 2. setting up pyhton enviroment

for setting up pyhton env run following command

```bash
> python -m venv <virtaul-env-name>
> <virtaul-env-name>\Scripts\activate
```

## 3. Intstalling all the required packages

you need to install all the packages persent inside requirements.txt for that run following command

```bash
pip install -r requirements.txt
```

## 4. setting up openai api key

first create a setup.py file and inser the code below inside it

```bash
setup_data = {
'OPENAI_API_KEY': '<YOUR_OPENAI_API_KEY>',
}
```

## 5. running the script

to start server run:

```bash
python server.py
```

## 6. checking output

1. install postman
2. open new tab with post request and paste `http://localhost:5000/summarize` in URL tab
3. inside body of url paste raw json data in format mentioned below

```bash
{
    "text_to_summarize":"<paragraph-that-is-to-be-summarized>"
}
```

### Points to remember

1. In this code some rate limits are applied and they are
   (i): 2 requests per minute
   (ii): 5 requests per day
2. Moderation API is also added in order to avoid input of explicit content
3. You can increase the number request per minute to run all tests or you can run some test individually
