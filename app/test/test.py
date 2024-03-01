from mockito import when, mock, unstub

when(os.path).exists('/foo').thenReturn(True)

# or:
import requests  # the famous library
# you actually want to return a Response-like obj, we'll fake it
response = mock({'status_code': 200, 'text': 'Ok'})
when(requests).get(...).thenReturn(response)

# use it
requests.get('http://google.com/')

# clean up
unstub()