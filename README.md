This tool returns a CSV file containing the username, first name, last name and title for each enumerated user.

<pre>
$ python LinkedInEnum.py
Usage: python LinkedInEnum.py CompanyID NumberOfPages
Example: python LinkedInEnum.py 1337 1000

*Find CompanyID by visiting a company page and copy the 1337 in:
	https://www.linkedin.com/company-beta/1337
	https://www.linkedin.com/company/1337
</pre>

Enumerating 10 LinkedIn search pages for LinkedIn employees:

<pre>
$ python LinkedInEnum.py 1337 10
 ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____
||L |||i |||n |||k |||e |||d |||I |||n |||E |||n |||u |||m ||
||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|
LinkedIn Username: leopold@rawbytesecurity.ca
LinkedIn Password:
[!] Authenticating...
[!] Authentication for "leopold@rawbytesecurity.ca" succeeded!
Username format options:
		1. Joe Schmo -> JoeSchmo
		2. Joe Schmo -> Joe.Schmo
		3. Joe Schmo -> JSchmo
		4. Joe Schmo -> J.Schmo
		5. Joe Schmo -> SchmoJoe
		6. Joe Schmo -> Schmo.Joe
		7. Joe Schmo -> SchmoJ
		8. Joe Schmo -> Schmo.J
Format Option: 3
You selected '3', proceed? [Y]es/No:
[!] Enumerating page number 1 for users...
[!] Enumerating page number 2 for users...
[!] Enumerating page number 3 for users...
[!] Enumerating page number 4 for users...
[!] Enumerating page number 5 for users...
[!] Enumerating page number 6 for users...
[!] Enumerating page number 7 for users...
[!] Enumerating page number 8 for users...
[!] Enumerating page number 9 for users...
[!] Enumerating page number 10 for users...
[!] User enumeration complete!
[!] 101 LinkedIn users were enumerated! Username, first name, last name and title was written to "/home/leo/Tools/Scripts/Repos/LinkedInEnum/1337_linkedin_users.csv"!
</pre>

<b>Please note:</b>
<ul>LinkedIn Terms of Service: "...we prohibit both the act of scraping others’ content from our services, and the development and support of tools to scrape LinkedIn services."</ul>
<ul>There is currently a bug that includes the current user apart of the user list (first entry).</ul>
<ul>You must use a LinkedIn account with a big enough network otherwise the search URL the script relies on will return unusable data.</ul>
<ul>The script uses a SLEEPMIN (line 31) and SLEEPMAX (line 32) to randomize the sleeps between HTTP requests, you can edit this, however, it is probably safer to leave the sleeps there.</ul>