import requests

url = "http://127.0.0.1:5000/sessions/1"
response = requests.delete(url)
print(response.json())