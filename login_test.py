import urllib.request

url = 'https://www.xpressleadpro.com/portal/public/signin/smillette@waysidepublishing.com/1894511/qualifiers'

with urllib.request.urlopen(url) as response:
    print(response.getcode())
