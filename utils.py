import tiktoken
from flask import request
from datetime import datetime
from setup import setup_data
import openai

openai.api_key = setup_data.get('OPENAI_API_KEY')
# if openai.api_key is not None:
#     print("api key found")
# else:
#     print("api key not found")

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def create_rate_limit_middleware(req_per_min, req_per_day, rate_limit_window, user_request_data, daily_request_count):
    def middleware(func):
        def wrapper(*args, **kwargs):
            user_ip = request.remote_addr
            now = datetime.now()           

            if user_ip not in user_request_data:
                user_request_data[user_ip] = [(now, 1)]
                daily_request_count[user_ip] = 1
            else:
                user_data = user_request_data[user_ip]
                user_data = [data for data in user_data if now - data[0] <= rate_limit_window]
                user_data.append((now, len(user_data) + 1))
                user_request_data[user_ip] = user_data

                if len(user_request_data[user_ip]) <= req_per_min:
                    daily_request_count[user_ip] = daily_request_count[user_ip] + 1

            if len(user_request_data[user_ip]) > req_per_min:
                user_request_data[user_ip].pop()
                return {'message': 'Requests per minute limit exceeded'}, 429
            
            if daily_request_count[user_ip] > req_per_day:
                return {"message": 'Daily requests limit exceeded'}, 429
            
            print(user_request_data[user_ip], daily_request_count[user_ip]) 

            return func(*args, **kwargs)
        
        return wrapper
    
    return middleware

def create_moderation_api_middleware(user_request_args):
    def middleware(func):
        def wrapper(*args, **kwargs):
            req = user_request_args.parse_args()
            # print(req)
            text_to_summarize = req.get('text_to_summarize')
            try:
                response = openai.Moderation.create(
                    input=text_to_summarize
                )
                output = response["results"][0]
                if output["flagged"] == True:
                    return {"error": "Bad Request", "message": "message contain some explicit content"}, 400
                else:
                    print("no explicit content")
                    return func(*args, **kwargs)
            except Exception as e:
                print(f"Err in moderation --> {e}")
                return {"error":"internal server error", "message": "some unexpected error occured. Please try again"}, 500

        return wrapper
    return middleware

def create_tokenlimiter_middleware(messages, user_request_args):
    def middleware(func):
        def wrapper(*args, **kwargs):
            req = user_request_args.parse_args()
            # print(req)
            text_to_summarize = req.get('text_to_summarize')
            messages[1]["content"] = text_to_summarize
            total_input_tokens = num_tokens_from_messages(messages=messages)
            print("total_input tokens: ", total_input_tokens)
            if total_input_tokens <= 250:
                return func(*args, **kwargs)
            else:
                return {"error": "Bad Request", "message": "token limit exceeded(less than 200 words)"}, 400
        return wrapper
    return middleware

