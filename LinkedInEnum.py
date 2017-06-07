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
def enum_users(response,csvWriter):
	"""
	Accepts a HTML response (string) and csv.writer object, writes data to the csv.writer object and returns the discovered users (list).
	"""
	global finalUserList
	global users
	global sharedConIDs
	global sharedConMiniProfileIDs
	tempUsers = []
	soup      = BeautifulSoup(response)
	codeList  = soup.findAll("code")
	for codeTag in codeList:
		codeText = codeTag.text
		escapedCode = htmlParse.unescape(codeText)
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
								sharedConMiniProfileIDs.append(miniProfileID)
				for userDetails in users:
					if not userDetails[3] in sharedConMiniProfileIDs:
						firstName  = userDetails[0]
						lastName   = userDetails[1]
						occupation = userDetails[2]
						userName   = format_username(firstName,lastName,formatOption)
						if (userName,firstName,lastName,occupation) not in finalUserList:
							finalUserList.append((userName,firstName,lastName,occupation))
							csvWriter.writerow((userName,firstName,lastName,occupation))
		except ValueError:
			pass
	return tempUsers
def format_username(firstName, lastName, formatOption):
	"""
	Accepts a first name (string), last name (string) and format option (integer) and returns the formatted username (string).

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
	return username
def get_format_option():
	"""
	Returns the chosen format option (int)
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
	return formatOption
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
	verbose                 = True
	users                   = []
	tempUsers               = []
	finalUserList           = []
	sharedConIDs            = []
	sharedConMiniProfileIDs = []
	htmlParse               = HTMLParser()
	username                = raw_input("LinkedIn Username: ")
	password                = getpass("LinkedIn Password: ")
	cookieJar               = login(username,password)
	formatOption            = get_format_option()
	outFileName             = os.path.join(os.getcwd(), str(TARGET_COMPANY)+"_linkedin_users.csv")
	outFile                 = open(outFileName,'w')
	csvWriter               = csv.writer(outFile)
	punctuation             = punctuation.replace('-','')
	punctuation            += ' '
	csvWriter.writerow(("Username", "First Name", "Last Name", "Position"))
	for pageNum in range(1,NUM_OF_PAGES+1):
		enumURL = "https://www.linkedin.com/search/results/people/?facetCurrentCompany=%%5B%%22%d%%22%%5D&page=%d" % (TARGET_COMPANY,pageNum)
		response = enum_page(enumURL,cookieJar,pageNum)
		if not response:
			if verbose: print Fore.YELLOW + "[!]" + Style.RESET_ALL + " Retrying page number %d..." % pageNum 
			response = enum_page(enumURL,cookieJar,pageNum)
			if not response:
				if verbose: print Fore.RED + "[!]" + Style.RESET_ALL + " Skipping page number %d..." % pageNum 
				continue
		tempUsers = enum_users(response,csvWriter)
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
		print Fore.GREEN + "[!]" + Style.RESET_ALL + " %d LinkedIn users were enumerated! First name, last name and title was written to \"%s\"!" % (len(finalUserList), os.path.join(os.getcwd(), outFileName))
	outFile.close()