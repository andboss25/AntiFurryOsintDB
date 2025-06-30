import requests
import json

f = requests.post("http://127.0.0.1/api/target/post",json={
    "start_vector_type":"username"
})

print(f.content)

target_id = json.loads(f.content)['Target']['Id']

f = requests.post("http://127.0.0.1/api/vector/post",json={
    "type":"username",
    "username":"andreiplsno",
    "platform":"youtube",
    "target_id":target_id,
    "is_starting":True
})

print(f.content)

