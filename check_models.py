
from dotenv import load_dotenv
from google import genai


load_dotenv()
client = genai.Client()

print("Models available for text generation:\n")

for model in client.models.list():
    actions = model.supported_actions or []

    if "generateContent" in actions:
        print(model.name)
