#!/usr/bin/python
import cookielib, csv, json, os, random, re, sys
from getpass import getpass
from HTMLParser import HTMLParser
from string import punctuation
from time import sleep
try:
	from colorama import Fore, Style
except:
	print "[ERROR] Please install the \"colorama\" module!"
	sys.exit(1)
try:
	import requests
	requests.packages.urllib3.disable_warnings()
except:
	print Fore.RED + "[ERROR]" + Style.RESET_ALL + " Please install the \"Requests\" module!"
	sys.exit(1)
try:
	import mechanize
except:
	print Fore.RED + "[ERROR]" + Style.RESET_ALL + " Please install the \"mechanize\" module!"
	sys.exit(1)
try:
	from BeautifulSoup import BeautifulSoup
except:
	print Fore.RED + "[ERROR]" + Style.RESET_ALL + " Please install the \"BeautifulSoup\" module!"
	sys.exit(1)
try:
	TARGET_COMPANY = int(sys.argv[1])
	NUM_OF_PAGES   = int(sys.argv[2])
	SLEEPMIN       = 4 #This will help not seem like a robot... :)...
	SLEEPMAX       = 12
except:
	print "Usage: python %s CompanyID NumberOfPages\nExample: python %s 1337 1000\n\n*Find CompanyID by visiting a company page and copy the 1337 in:\n\thttps://www.linkedin.com/company-beta/1337\n\thttps://www.linkedin.com/company/1337" % (sys.argv[0], sys.argv[0])
	sys.exit(1)
def are_you_sure(question, validOptions=()):
	"""
	Accepts a question (string) and valid options (tuple) and returns the answer (string).
	"""
	areYouSure = 'No'
	while yes_or_no(areYouSure) == False:
		answer = raw_input(question)
		areYouSure   = raw_input("You selected '%s', proceed? [Y]es/No: " % answer)
		if yes_or_no(areYouSure) == True:
			try:
				if answer in validOptions:
					return answer
				else:
					print Fore.RED + "[!]" + Style.RESET_ALL + " Invalid format option!"
					areYouSure = 'No'
			except:
				print Fore.RED + "[!]" + Style.RESET_ALL + " Invalid format option!"
				areYouSure = 'No'
def convert_to_usernames(LinkedInDataFileName):
	"""
	Accepts a file name (string) to the source LinkedIn data file and writes formatted usernames to a txt file.
	"""
	print """Username format options:
		1. Joe Schmo -> JoeSchmo
		2. Joe Schmo -> Joe.Schmo
		3. Joe Schmo -> JSchmo
		4. Joe Schmo -> J.Schmo
		5. Joe Schmo -> SchmoJoe
		6. Joe Schmo -> Schmo.Joe
		7. Joe Schmo -> SchmoJ
		8. Joe Schmo -> Schmo.J"""
	validOptions = ('1','2','3','4','5','6','7','8')
	formatOption = int(are_you_sure("Format Option: ", validOptions))
	usernames = get_formatted_usernames(LinkedInDataFileName, formatOption)
	outFileName = str(TARGET_COMPANY)+"_usernames.txt"
	outFile = open(outFileName,'w')
	for username in usernames:
		outFile.write(username+'\n')
	outFile.close()
	print Fore.GREEN + "[!]" + Style.RESET_ALL + " %d usernames written to \"%s\"!" % (len(finalUserList), os.path.join(os.getcwd(), outFileName))
def encode_string(inputString):
	"""
	Accepts a string and returns the string with proper encoding (ASCII, UTF-8, UTF-16)
	"""
	try:
		inputString = inputString.encode("ascii")
	except:
		try:
			inputString = inputString.encode("utf-8", 'ignore')
		except:
			try:
				inputString = inputString.encode("utf-16", 'ignore')
			except:
				print Fore.RED + "[ERROR]" + Style.RESET_ALL + " Can't decode the \"%s\" variable..." % inputString
				sys.exit(1)
	return inputString
def enum_page(enumURL,cookieJar,pageNum):
	"""
	Accepts a URL (string), CookieJar object and page number (int) and returns the response (string).
	"""
	if verbose: print Fore.YELLOW + "[!]" + Style.RESET_ALL + " Enumerating page number %d for users..." % pageNum
	try:
		response = get_request(enumURL,cookieJar)
	except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
		if verbose: print Fore.YELLOW + "[!]" + Style.RESET_ALL + " Retrying page number %d..." % pageNum 
		try:
			response = get_request(enumURL,cookieJar)
		except:
			if verbose: print Fore.RED + "[!]" + Style.RESET_ALL + " Skipping page number %d..." % pageNum 
			return None
	return response
def enum_users(result):
	"""
	Accepts a JSON string and appends discovered LinkedIn users to the global 'users' variable.
	"""
	global users
	title = temptitle = ''
	if 'person' in result.keys() and 'firstName' in result['person'].keys() and 'lastName' in result['person'].keys():
		firstName = result['person']['firstName']
		lastName = result['person']['lastName']
		snips = result['person']['snippets']
		for snip in snips:
			if 'fieldName' in snip.keys() and 'heading' in snip.keys() and snip['fieldName'] == 'Current':
				title = temptitle = snip['heading']
				title = title.replace('<B>','').replace('</B>', '').split(' at')[0]
				break
		company = ''
		startBoldTagIndex = temptitle.find('<B>')
		while startBoldTagIndex >= 0:
			endBoldTagIndex   = temptitle[startBoldTagIndex:].find('</B>') + startBoldTagIndex
			company += temptitle[startBoldTagIndex+len('<B>'):endBoldTagIndex]
			temptitle = temptitle[endBoldTagIndex+len('</B>'):]
			startBoldTagIndex = temptitle.find('<B>')
			if startBoldTagIndex >= 0:
				company += temptitle[:startBoldTagIndex]
		if (firstName,lastName,title) not in users:
			firstName = firstName.split()[0]
			lastName  = lastName.split(',')[0]
			firstName = encode_string(firstName)
			lastName  = encode_string(lastName)
			title     = encode_string(title)
			users.append((firstName,lastName,title))
def get_formatted_usernames(inputFileName, formatOption):
	"""
	Accepts a csv input file name (string) and format option (integer) and returns formatted usernames (list).

	Username format options:
	1. Joe Schmo -> JoeSchmo
	2. Joe Schmo -> Joe.Schmo
	3. Joe Schmo -> JSchmo
	4. Joe Schmo -> J.Schmo
	5. Joe Schmo -> SchmoJoe
	6. Joe Schmo -> Schmo.Joe
	7. Joe Schmo -> SchmoJ
	8. Joe Schmo -> Schmo.J
	"""
	try:
		inputFile = open(inputFileName)
		csvReader = csv.reader(inputFile)
	except:
		raise Exception("Invalid input file name!")
	usernames = []
	for row in csvReader:
		firstName = row[0]
		lastName  = row[1]
		position  = row[2]
		if firstName == "First Name" and lastName == "Last Name" and position == "Position":
			continue #Skip first entry...
		lastName  = ''.join(lastName.split(' '))
		if formatOption == 1:
			username = firstName + lastName
		elif formatOption == 2:
			username = firstName + '.' + lastName
		elif formatOption == 3:
			username = firstName[:1] + lastName
		elif formatOption == 4:
			username = firstName[:1] + '.' + lastName
		elif formatOption == 5:
			username = lastName + firstName
		elif formatOption == 6:
			username = lastName + '.' + firstName
		elif formatOption == 7:
			username = lastName + firstName[:1]
		elif formatOption == 8:
			username = lastName + '.' + firstName[:1]
		else:
			raise Exception("Invalid format option!")
		if username not in usernames: usernames.append(username)
	inputFile.close()
	return usernames
def get_request(url, cookieJar={}):
	"""
	Accepts a URL and returns HTML (string).
	"""
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0'
	}
	sleep(random.uniform(SLEEPMIN,SLEEPMAX)) #Searching for users via scraping violates the terms of service... 
	response = requests.get(url, verify=True, headers=headers, timeout=1, allow_redirects=True, cookies=cookieJar)
	HTML     = response.text
	return HTML
def login(username, password, verbose=True):
	"""
	Accepts a username (string), password (string), and verbosity (boolean) respectively and returns a Cookie Jar object.
	"""
	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	browser.addheaders = [
		('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0')
	]
	cookieJar = cookielib.LWPCookieJar()
	browser.set_cookiejar(cookieJar)
	browser.open("https://www.linkedin.com/")
	browser.select_form(nr=0)
	browser["session_key"] = username
	browser["session_password"] = password
	if verbose: print Fore.YELLOW + "[!]" + Style.RESET_ALL + " Authenticating..."
	sleep(random.uniform(SLEEPMIN,SLEEPMAX)) #Searching for users via scraping violates the terms of service...
	response = browser.submit()
	try:
		li_at = requests.utils.dict_from_cookiejar(cookieJar)['li_at']
		if verbose: print Fore.GREEN + "[!]" + Style.RESET_ALL + " Authentication for \"%s\" succeeded!" % username
		return cookieJar
	except:
		if verbose: print Fore.RED + "[ERROR]" + Style.RESET_ALL + " Authentication failed!"
		sys.exit(1)
def yes_or_no(option):
	"""
	Accepts a option (string), and returns a True/False (boolean) to prompt for yes/no.
	"""
	yes = set(['yes','y', 'ye', ''])
	no = set(['no','n'])
	option = option.lower()
	if option in yes:
		return True
	elif option in no:
		return False
	else:
		return True
if __name__ == "__main__":
	print ' ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ \n||L |||i |||n |||k |||e |||d |||I |||n |||E |||n |||u |||m ||\n||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__||\n|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|'
	verbose                = True
	finalUserList          = []
	tempUsers              = []
	users                  = []
	sharedConIDs           = []
	shareConMiniProfileIDs = []
	username               = raw_input("LinkedIn Username: ")
	password               = getpass("LinkedIn Password: ")
	cookieJar              = login(username,password)
	h                      = HTMLParser()
	punctuation            = punctuation.replace('-','')
	punctuation           += ' '
	for pageNum in range(1,NUM_OF_PAGES+1):
		tempUsers = []
		enumURL = "https://www.linkedin.com/search/results/people/?facetCurrentCompany=%%5B%%22%d%%22%%5D&page=%d" % (TARGET_COMPANY,pageNum)
		response = enum_page(enumURL,cookieJar,pageNum)
		if not response: continue
		soup = BeautifulSoup(response)
		codeList  = soup.findAll("code")
		for codeTag in codeList:
			codeText = codeTag.text
			escapedCode = h.unescape(codeText)
			try:
				parsedJSON = json.loads(escapedCode)
				if 'included' in parsedJSON.keys():
					for entry in parsedJSON['included']:
						if 'firstName' in entry.keys() and 'lastName' in entry.keys() and 'occupation' in entry.keys() and 'entityUrn' in entry.keys() and 'objectUrn' in entry.keys():
							discoveredUser = (''.join([c for c in list(encode_string(entry['firstName']).split()[0]) if c not in punctuation]), ''.join([c for c in list(encode_string(entry['lastName']).split(',')[0]) if c not in punctuation]), ' '.join(encode_string(entry['occupation']).split()), encode_string(entry['entityUrn']).split(':')[-1], encode_string(entry['objectUrn']).split(':')[-1])
							if discoveredUser not in users:
								tempUsers.append(discoveredUser)
								users.append(discoveredUser)
					for entry in parsedJSON['included']:
						if 'entityUrn' in entry.keys() and 'sharedConnections' in entry.keys():
							for fN, lN, occ, entUrn, objUrn in users:
								if objUrn == entry['entityUrn'].split(':')[-1]:
									for sharedConnection in entry['sharedConnections']:
										sharedConID = sharedConnection.split(',')[-1]
										if sharedConID not in sharedConIDs:
											sharedConIDs.append(sharedConID)
					for entry in parsedJSON['included']:
						if '$id' in entry.keys() and '$type' in entry.keys() and 'miniProfile' in entry.keys() and 'distance' in entry.keys():
							for sharedConID in sharedConIDs:
								if sharedConID == entry['$id'].split(',')[-1]:
									miniProfileID = entry['miniProfile'].split(':')[-1]
									shareConMiniProfileIDs.append(miniProfileID)
					for userDetails in users:
						if not userDetails[3] in shareConMiniProfileIDs:
							if userDetails not in finalUserList:
								finalUserList.append(userDetails)
			except:
				pass
		if not len(tempUsers):
			if verbose:
				if pageNum == 1:
					errorMsg = " No matches found..."
				else:
					errorMsg = " No more matches found..."
				print Fore.RED + "[!]" + Style.RESET_ALL + errorMsg
			break
	if verbose: print Fore.GREEN + "[!]" + Style.RESET_ALL + " User enumeration complete!"
	if len(finalUserList) == 0:
		print Fore.RED + "[!]" + Style.RESET_ALL + " 0 LinkedIn users were enumerated..."
		sys.exit(1)
	else:
		outFileName = os.path.join(os.getcwd(), str(TARGET_COMPANY)+"_linkedin_users.csv")
		outFile = open(outFileName,'w')
		csvWriter = csv.writer(outFile)
		csvWriter.writerow(("First Name", "Last Name", "Position"))
		for firstName, lastName, title, entUrn, objUrn in finalUserList:
			csvWriter.writerow((firstName,lastName,title))
		outFile.close()
		print Fore.GREEN + "[!]" + Style.RESET_ALL + " %d LinkedIn users were enumerated! First name, last name and title was written to \"%s\"!" % (len(finalUserList), os.path.join(os.getcwd(), outFileName))
		convert_to_usernames(outFileName)
