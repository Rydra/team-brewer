import os

from slackclient import SlackClient


class SlackNotifier:
    def notify(self, message):
        slack_token = os.environ["SLACK_API_TOKEN"]
        sc = SlackClient(slack_token)

        sc.api_call(
            "chat.postMessage",
            channel="#team-brewer",
            text=f"@here\n```{message}```",
            as_user=True
        )