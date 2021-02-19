import json
from queue import Queue
from threading import Thread
import requests
import multiprocessing as mp
from bs4 import BeautifulSoup

url = 'https://namemc.com/search?q='
data = {
    'dupes': dict()
}
concurrent = 4
q = Queue(concurrent * 2)

nameq = mp.Queue()
for _next in json.loads(open('commonusers.json').read()):
    nameq.put(_next)

def find(nameq):
    user = nameq.get()
    global data
    while user != None:
        name = 0
        uuids = []
        r = requests.get(url + user)
        re = r.content
        soup = BeautifulSoup(re, 'html.parser')
        print()
        print('\nsending user: ' + user)
        for h in soup.find_all('h3'):
            print(h.text.strip())
            if h.text.strip().lower() == user.lower():
                uuids.append(soup.select('samp')[name + 1].text)
                name += 1

        if name > 1:
            print("Dupe")
            data['dupes'][user.strip()] = {
                'uuids': uuids,
                'count': name,
                'url': f'https://namemc.com/search?q={user}',
                'searches': soup.select('.tabular')[0].text
            }
        user = nameq.get()



_threads = []
for i in range(concurrent):
    _threads.append(Thread(target=find, daemon=True, args=(nameq,)))
    _threads[i].start()

for i in range(concurrent):
    _threads[i].join()

with open('dupes.txt', 'w') as outfile:
    outfile.write(json.dumps(data, indent=4))
    outfile.close()
