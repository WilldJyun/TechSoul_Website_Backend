import requests

message = requests.get("http://localhost:5000/api/pic?name=intro.jpg")
print(message.text)