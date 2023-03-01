import requests, json

def get_kisan_youtube_link():
    url_tv = 'http://prasarbharati.org/pb/code/index.php/channels/getTvChannels'
    r = requests.get(url_tv)
    for i in json.loads(r.text)['payload']['tvlist']:
        if i['title'] == 'DD Kisan LIVE 24x7':
            print(i['link'])

def get_radio_src():
    url_radio = 'http://prasarbharati.org/pb/code/index.php/channels/getRadioChannels'
    r = requests.get(url_radio)
    #print(json.loads(r.text)['payload']['radiolist'])
    for i in json.loads(r.text)['payload']['radiolist']:
        print(i['id'],i['title'],i['location'],i['statename'])
get_radio_src()

'''
{'id': '323SIL', 'title': 'AIR Siliguri',
 'link': 'http://air.pc.cdn.bitgravity.com/air/live/pbaudio164/playlist.m3u8',
 'description': 'AIR Siliguri', 'thumbnail': 'http://prasarbharati.org/pb/images/RADIO_229808.jpg',
 'category': 'NEWS', 'classification': None,
 'android_compatible': 'YES', 'ios_compatible': 'NO',
 'language': 'Bangla', 'latitude': '26.73',
 'longitude': '88.43666667', 'location': 'SILIGURI',
 'statename': 'WEST BENGAL', 'disp_order': '5',
 'mediaid': '323', 'facebook_link': None,
 'twitter_link': None, 'prg_guide': None}
'''





#with open("radiochannels.py","w") as f:
#    f.write(json.loads(r.text))
