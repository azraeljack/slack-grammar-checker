# Grammar Checker Slack Bot

This is an AIGC project by GPT-4, it writes everything including this doc, I just tweaked a little bit of the prompt by myself. If you found any issues, you can ask ChatGPT to fix it for you.

This Slack bot is designed to check and correct English grammar in Slack messages. It uses OpenAI's GPT-3.5 Turbo model for text processing.

## Setup Instructions

### Step 1: Create a new App in Slack

1. Visit the Slack API website and click on `Your Apps`.
2. Click on `Create New App` button, name your app, and select the workspace you want to install it in.
3. Navigate to `OAuth & Permissions` page under the `Features` section in the sidebar. Here, add the following scopes under `Bot Token Scopes`:
    - `channels:history`
    - `channels:read`
    - `channels:write`
    - `chat:write`
    - `chat:write.public`
    - `users:read`
4. Click `Install to Workspace` button. You will be redirected to your workspace to authorize the app. Allow it.
5. Once installed, you will be redirected back to the `OAuth & Permissions` page. Here, you can find your `Bot User OAuth Access Token`. Save this token, you'll need it later.
6. From your app's settings page, navigate to the `Basic Information` section.
7. Scroll down to find the `App Credentials` section. Here, you can find your `Signing Secret`. Save this token, you'll need it later.

### Step 2: Create a configuration file

Create a `.env` file in your project directory with the following contents:

```shell
SLACK_BOT_TOKEN=your-bot-user-oauth-access-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
OPENAI_API_KEY=your-openai-api-key
```

Replace `your-bot-user-oauth-access-token` and `your-slack-signing-secret` with the token you saved earlier and `your-openai-api-key` with your OpenAI API key.

### Step 3: Run the bot

To run the bot locally, first install the dependencies using pipenv:

```shell
pipenv install
pipenv run python app.py
```

Now the bot is running.

### Step 4: Configure Request URL in Slack

After you have your public URL, go back to your app settings on Slack API website.
Navigate to 'Event Subscriptions' under the 'Features' section in the sidebar. Here, enable events.
In the `Request URL` box, enter your public URL followed by /slack/events. For example, if your public URL is https://12345.ngrok.io, enter https://12345.ngrok.io/slack/events as the `Request URL`.
Under `Subscribe to Bot Events`, click on the `Add Bot User Event` button and add `message.channels` event.
Finally, reinstall your app to your workspace for these changes to take effect.

## Usage

Once the bot is running and installed to your workspace, it will automatically check and correct the grammar of all English messages sent in the channels it's added to.

Please note that the bot will only correct English messages and will ignore messages that contain non-English characters.
