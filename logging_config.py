# logging_config.py

import logging
import requests

# Custom Slack Handler to send logs to Slack
class SlackHandler(logging.Handler):
    def __init__(self, webhook_url, level=logging.ERROR):
        super().__init__(level)
        self.webhook_url = webhook_url

    def emit(self, record):
        log_entry = self.format(record)
        try:
            response = requests.post(self.webhook_url, json={'text': log_entry}, timeout=5)
            if response.status_code != 200:
                raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
        except Exception as e:
            print(f"Failed to send log to Slack: {e}")

# Slack Webhook URL (replace with your actual webhook URL)
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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'

# Logging configuration function
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers = []

    # Add Slack handler for error and critical levels
    slack_handler = SlackHandler(webhook_url=SLACK_WEBHOOK_URL, level=logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    slack_handler.setFormatter(formatter)
    logger.addHandler(slack_handler)

# Function to send custom messages (including data) to Slack
def send_to_slack(message):
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={'text': message}, timeout=5)
        if response.status_code != 200:
            raise ValueError(f"Slack returned an error {response.status_code}, response: {response.text}")
    except Exception as e:
        logging.error(f"Failed to send message to Slack: {e}")
