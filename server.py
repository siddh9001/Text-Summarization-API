from setup import setup_data
from flask import Flask
from flask_restful import Api, Resource, reqparse
import openai
from utils import create_rate_limit_middleware, create_moderation_api_middleware, create_tokenlimiter_middleware
from datetime import timedelta

openai.api_key = setup_data.get('OPENAI_API_KEY')
if openai.api_key is not None:
    print("api key found")
else:
    print("api key not found")

app = Flask(__name__)
api = Api(app)

request_post_args = reqparse.RequestParser()
request_post_args.add_argument("text_to_summarize", type=str, help="the text that is to be summarized", required=True)



system_message = f"summarize the user message in less than 100 words"

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 150
REQUEST_PER_DAY = 5
REQUEST_PER_MINUTE = 2
RATE_LIMIT_WINDOW = timedelta(minutes=1)

rate_limit_middleware = create_rate_limit_middleware(req_per_min=REQUEST_PER_MINUTE, req_per_day=REQUEST_PER_DAY, rate_limit_window=RATE_LIMIT_WINDOW)

messages = [
    {"role" : "system", "content": system_message},
    {"role": "user", "content": None},
]

def chat_completion_helper_function(messages):
    try:
        response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.0,
        max_tokens=MAX_TOKENS, 
        )
        print(response["usage"])
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Err in chatCompletion --> {e}"


class SummarizationAPI(Resource):
    def get(self):
        return {"text": "this is summrization api"}
    
    @rate_limit_middleware
    @create_tokenlimiter_middleware(messages=messages, user_request_args=request_post_args)
    # @create_moderation_api_middleware(request_post_args)
    def post(self):
        args = request_post_args.parse_args()
        messages[1]["content"] = args["text_to_summarize"]
        # chat_response = chat_completion_helper_function(messages=messages)
        # return {"summarized_text": chat_response}
        return {"success":True}


api.add_resource(SummarizationAPI, "/summarize")

if __name__ == "__main__":
    app.run(debug=True)