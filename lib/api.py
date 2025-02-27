import requests

def load_densha_info(api_url, route_name):
    api_url = f'{api_url}/densha/routes/?search={route_name}'
    response = requests.get(api_url)
    densha_info = response.json()
    return densha_info