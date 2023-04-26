import configparser

import requests
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, \
    ResultReason, CancellationReason
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application


def speech_synthesis_to_wave_file(text: str):
    """performs speech synthesis to a wave file"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    subscription_key = config.get('AZURE', 'SPEECH_KEY')
    region = config.get('AZURE', 'SPEECH_REGION')
    print(f'KEY：{subscription_key}, REGION:{region}')
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_synthesis_voice_name = "zh-CN-YunfengNeural"
    # Creates a speech synthesizer using file as audio output.
    # Replace with your own audio file name.
    file_name = "outputaudio.wav"
    file_config = AudioOutputConfig(filename=file_name)
    speech_synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)



    # use the default speaker as audio output.
    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

            print("Error details: {}".format(cancellation_details.error_details))

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
    files = {'sample': open("outputaudio.wav", 'rb')}
    data = {
        'fPitchChange': '1',
        'sampleRate': '44100'
    }
    response = requests.post('http://121.41.44.246:7860/voiceChangeModel', files=files, data=data)
    await update.message.reply_voice(voice=response.content)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    config = configparser.ConfigParser()
    config.read('config.ini')
    application = Application.builder().token(config.get('TELEGRAM', 'TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("speak", speak))
    application.run_polling()

if __name__ == '__main__':
    main()
