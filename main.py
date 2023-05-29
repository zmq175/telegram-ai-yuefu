import configparser
import xml.etree.ElementTree as ET

import requests
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application


def speech_synthesis_to_wave_file(text: str):
    config = configparser.ConfigParser()
    config.read('config.ini')
    subscription_key = config.get('AZURE', 'SPEECH_KEY')
    region = config.get('AZURE', 'SPEECH_REGION')
    print(f'KEY：{subscription_key}, REGION:{region}')

    # construct request body in SSML format
    ssml = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-YunfengNeural'>" \
           + text + "</voice></speak>"

    headers = {
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "YOUR_RESOURCE_NAME",
        "Authorization": "Bearer " + get_token(subscription_key, region)
    }

    # send the request and get the response
    response = requests.post(
        "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1",
        headers=headers,
        data=ssml.encode('utf-8')
    )

    # check the response
    if response.status_code == 200:
        with open("outputaudio.wav", "wb") as f:
            f.write(response.content)
        print("Speech synthesized for text [{}]".format(text))
    else:
        print("Error synthesizing speech: {}".format(response.text))


def get_token(subscription_key, region):
    # construct request URL and headers
    url = "https://" + region + ".api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key
    }

    # send the request and get the response
    response = requests.post(url, headers=headers)

    # extract token from the response
    if response.status_code == 200:
        print("get token succeed")
        return response.text
    else:
        print("get token failed")
        raise ValueError("Failed to get token: {}".format(response.text))


async def start(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi!')


async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert text to speech and send it as a voice message."""
    # Get user input text
    user_input = " ".join(context.args)
    print(user_input)

    speech_synthesis_to_wave_file(user_input)

    # Upload to third-party service
    files = [
        ('sample', (
            'outputaudio.wav', open('outputaudio.wav', 'rb'),
            'audio/wav'))
    ]
    url = "https://u99742-9438-6a636289.neimeng.seetacloud.com:6443/voiceChangeModel"

    payload = {'fPitchChange': '1',
               'sampleRate': '44100'}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code != 200:
        print(response.text)
    await update.message.reply_voice(voice=response.content)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    config = configparser.ConfigParser()
    config.read('config.ini')
    application = Application.builder().token(config.get('TELEGRAM', 'TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("speak", speak))
    print("start polling")
    application.run_polling()


if __name__ == '__main__':
    main()
