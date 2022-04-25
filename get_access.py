from pocket import Pocket
import webbrowser

# put your application's consumer key here
consumer_key = '1234-abcd1234abcd1234abcd1234'

request_token = Pocket.get_request_token(consumer_key)

auth_url = Pocket.get_auth_url(request_token)
webbrowser.open(auth_url)
input('An authorization page was open, after authorizing press enter.')

user_credentials = Pocket.get_credentials(consumer_key, request_token)
print('Your access token: ' + user_credentials['access_token'])
