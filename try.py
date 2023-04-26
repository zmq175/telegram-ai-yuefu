import requests

url = "https://u9c50-6a4b59ba.neimeng.seetacloud.com:6443/voiceChangeModel"

payload = {'fPitchChange': '1',
'sampleRate': '44100'}
files=[
  ('sample',('output.wav',open('outputaudio.wav','rb'),'audio/wav'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
