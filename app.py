import logging
import os
import string

import openai
from cachetools import TTLCache
from flask import Flask, request, make_response
from openai import OpenAIError
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

# Set up logging
logging.basicConfig(level=logging.INFO)

slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
signature_verifier = SignatureVerifier(slack_signing_secret)
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=slack_bot_token)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create a cache that will store up to 10000 items, each item will live 1 hour
cache = TTLCache(maxsize=10000, ttl=3600)

app = Flask(__name__)


def is_english(text):
    text_without_punctuations = ''.join(e for e in text if e.isalpha() or e.isspace())
    text_without_punctuations_and_spaces = text_without_punctuations.replace(' ', '')
    return all(c in string.ascii_letters for c in text_without_punctuations_and_spaces)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)

    event = request.json
    if "challenge" in event:
        return make_response(event["challenge"], 200, {"content_type": "application/json"})

    if "event" not in event:
        return make_response("no event found in request", 400)

    event = event["event"]

    if event.get("subtype") == "bot_message":
        logging.info(f"Ignored bot message")
        return make_response("", 200)

    user = event["user"]
    text = event["text"]
    channel = event["channel"]
    client_msg_id = event.get('client_msg_id')

    if client_msg_id in cache:
        # This message has been processed before
        logging.info(f"Ignored repeated message with client_msg_id {client_msg_id}")
        return make_response("", 200)

    cache[client_msg_id] = 1
    if not is_english(text):
        logging.info(f"Message is not english, {text}")
        return make_response("", 200)

    logging.info(f"Processing message with client_msg_id {client_msg_id}")

    correction = get_correction(text)

    if channel[0] == 'D':  # Direct message, use chat_postMessage
        slack_client.chat_postMessage(
            channel=channel,
            text=correction
        )
    else:  # In channel, use chat_postEphemeral
        slack_client.chat_postEphemeral(
            channel=channel,
            user=user,
            text=correction
        )

    return make_response("", 200)


def get_correction(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant that understands English grammar well. "
                                              "Your task is to identify any grammatical errors in the user's message "
                                              "and suggest corrections."},
                {"role": "user", "content": message},
                {"role": "assistant", "content": "Could you please review the grammar in the previous message, list "
                                                 "all the corrections, highlight why it is not correct, "
                                                 "and output the correct content. "
                                                 "The output format should be compatible "
                                                 "with markdown grammar in Slack."
                 },
            ],
        )
    except OpenAIError as e:
        return str(e)
    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
