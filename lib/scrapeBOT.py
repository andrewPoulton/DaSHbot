from bs4 import BeautifulSoup
import lxml
import bs4
import re, os, json
import urllib.request
import requests
from dateutil import parser
from datetime import datetime, date
import moment, calendar
import csv
from slackclient import SlackClient
import botguts
from pocket import Pocket, PocketException







def smmry(link,smm):
    apilink = "http://api.smmry.com/&SM_API_KEY=" + smm + "&SM_LENGTH=5&SM_URL=" + link
    tesSUM = requests.get(apilink)
    return tesSUM.json()
    


def is_valid_date(string):
	today = datetime.today()
	try:
		x = parser.parse(string).replace(tzinfo=None)
		if 1000 > (today - x).days > 0 :
			return x.date()
	except ValueError:
		return False
	return False

def is_date(string):
	try:
		x = parser.parse(string)
		return True
	except ValueError:
		return False

def find_date(string):
    string = string.split(' ')
    l = len(string)
    for k in range(l):
        if is_date(string[k]):
            i=k
            j=k+1
            while is_date(' '.join(string[i:j])) and j<l+1:
                j+=1  
            return is_valid_date(' '.join(string[i:j-1]))
    return False

def galink(link):
	if re.search('&ct=', link):
		return re.findall(r'&url=(.*?)&ct=', link)[0]
	else:
		return link

def runDMC(command):
	filestring, chan = command.split("chan=")
	d = find_date(filestring)
	since = None
	if d:
		since = calendar.timegm(d.timetuple())
	print(since)
	#command, filestring, chan, user = command.split(" ")
	#print(command, filestring, chan, user)
	slack_client=SlackClient(os.environ.get('ANDY_TOKEN'))
	
	c_key = os.environ.get("POCKET_TOKEN")
	cc_toke = os.environ.get("COXON_POCKET")
	print(c_key, cc_toke)
	#if is_date(since):
	#	since = parser.parse(since).timestamp()
	p = Pocket(consumer_key = c_key, access_token = cc_toke)
	try:
		poks = p.retrieve(sort = 'newest', detailType = 'complete', since = since) #tag, since parameters too
	except PocketException as e:
		print(e.message)
		return "Uh-oh.  I've had a problem trying to look in your Pocket."
	ad = []
	print(poks)
	for key in poks['list']:
		ad.append(key)

	links = [poks['list'][a]['resolved_url'] for a in ad if 'resolved_url' in poks['list'][a]]
	tt = [poks['list'][a]['resolved_title'] for a in ad if 'resolved_title' in poks['list'][a]]
	
	
	SMMRY_API = os.environ.get('SMMRY_API')
		
	lRow = []

	for link in links:
		lDict = {'Topic':"", 'Date Added':datetime.today().date(), 'Date of Material':"", 'Contributor':"SlackBot", 'Type':"Google Alert News", 'Link(s)':"", 'Title or Brief Description':"", 'Summary':""}
		lDict['Link(s)'] = link
		if filestring == 'pocket':
			lDict['Title or Brief Description'] = tt[len(lRow)]
		e = requests.get(link) #error handle here, pdf check?
		e = BeautifulSoup(e.text,'html.parser')
		for thing in e(["script","style","head","a"]):
			thing.extract()
		text = e.get_text()
		lines = (line.strip().replace('.',':') for line in text.splitlines())
		#chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
		textOut = '\n'.join(line for line in lines if line)
		
		dates = [is_date(line) for line in lines]
		if len(dates)>0:
			#print(dates[0])
			lDict['Date of Material'] = dates[0]
		else:
			for line in textOut.split('\n'):
				#print(line)
				if find_date(line):
					#print(find_date(line))
					lDict['Date of Material'] = find_date(line)
					break
		summary = ""#smmry(link, SMMRY_API)
		if 'sm_api_title' in summary:
			lDict['Title or Brief Description'] = summary['sm_api_title']
			lDict['Summary'] = summary['sm_api_content'].replace(".", ".\n\n")
		else:
			titles = [cand.get_text().strip() for cand in e("h1")][::-1]
		#print(titles)
			while len(titles)>0:
				if len(titles[-1])>0 and filestring!='pocket':
				#print(titles[-1])
					lDict['Title or Brief Description'] = titles[-1]
					break
				titles.pop()

		lRow.append(lDict)
		#print(lDict)
		#print(lRow)
	#print(lRow)
	tstamp = moment.now().format('MMM_DD_YYYY')
	with open(tstamp + '_bot_summary.csv', 'w') as csvfile:
		fieldnames = ['Topic', 'Date Added', 'Date of Material', 'Contributor', 'Type', 'Link(s)', 'Title or Brief Description', 'Summary']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in lRow:
			writer.writerow(row)
	with open(tstamp + '_bot_summary.csv', 'r') as csvfile:	
		testf = slack_client.api_call("files.upload", file = csvfile, filename = tstamp + '_bot_summary.csv', channels = chan)
	#print(testf)
	return "There you go!"
	
bot_commands = []
#if __name__ == '__main__':
#	runDMC('links', "D4Q21M79C")
def sayHI(*args):
	return args[0]
	
scraper = botguts.Bot_Command('summar', runDMC)
bot_commands.append(scraper)
