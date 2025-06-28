import requests

def get_ws_endpoint():
    url = "https://api-futures.kucoin.com/api/v1/bullet-public"
    response = requests.post(url)  # This sends the POST request
    data = response.json()
    if data["code"] == "200000":
        token = data["data"]["token"]
        endpoint = data["data"]["instanceServers"][0]["endpoint"]
        print("Websocket endpoint:", endpoint)
        print("Token:", token)
        return endpoint, token
    else:
        print("Error:", data)
        return None, None

if __name__ == "__main__":
    get_ws_endpoint()