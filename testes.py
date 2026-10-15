import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzkyMDIyOTQwfQ.nfTdlWShmHGbYW1QRed7JMxLaIJfKFynn021M1sN44o"
}

requisicao = requests.get("http://localhost:9533/auth/refresh", headers=headers)

print(requisicao.json())