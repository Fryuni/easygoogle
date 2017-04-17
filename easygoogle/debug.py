from pickle import load, dump
from os.path import dirname, join
from re import compile as rExcompile, findall
from urllib.request import Request as req, urlopen as uopen

with open(join(dirname(__file__), 'apis.pk'), 'rb') as fl:
	apis = load(fl)

def config():
    prevnames = {y['scope']:x for x, y in apis.items()}
    
    pgdata =uopen(req('https://developers.google.com/api-client-library/python/apis/', headers={'User-Agent': 'easyGoogle python api configurator'}))
    for _ in range(1230):
        pgdata.readline()
    findings = findall("<td>(.+?)</td>\s+?<td>(.+?)</td>\s+?<td><a href=\"https://developers.google.com/api-client-library/python.+?\">(v.+?)</a></td>", pgdata.read().decode())
    
    python_confirmed = {x[0]:(x[1], x[2]) for x in findings}
    
    pgdata = uopen(req('https://developers.google.com/identity/protocols/googlescopes', headers={'User-Agent': 'easyGoogle python api configurator'}))
    for _ in range(750):
        pgdata.readline()
    
    rx_header = rExcompile("\\s*<h2.*?<a href=.*?\">(.+? API)</a>, (v.+?)</h2>")
    
    while pgdata.length > 0:
        line = pgdata.readline().decode()
        match_header = rx_header.match(line)
        if match_header:
            if python_confirmed[match_header.group(1)]:
            print("Header found: %s --> %s" % match_header.group(1, 2))
        

def lis():
	return '\n'.join(sorted(apis.keys()))
	
def get(scps):
	if scps is str:
		scps = (scps,)
	return ','.join([apis[s]['scope'] for s in scps])
	
if __name__=="__main__":
	from sys import argv
	if len(argv) >= 2:
		if argv[1] == 'list':
			print(lis())
		elif argv[1] == 'form':
			with open(join(dirname(__file__), 'scopedump.txt'), 'w') as fl:
				fl.write(get(argv[2:]))
			print(get(argv[2:]))
		else:
			print(get(argv[1]))
		exit()
	config()