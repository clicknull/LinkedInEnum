A simple tool that accepts a LinkedIn "Company ID" and number of pages as positional arguments and LinkedIn credentials as interactive input. The tool returns a CSV file containing first name, last name and position for each enumerated user as well as a list of formatted usernames that can be used for password spraying, phishing, etc.

<pre>
$ python LinkedInUserEnum.py
Usage: python LinkedInUserEnum.py CompanyID NumberOfPages
Example: python LinkedInUserEnum.py 1337 1000

*Find CompanyID by visiting a company page and copy the 1337 in:
	https://www.linkedin.com/company-beta/1337
	https://www.linkedin.com/company/1337
</pre>

Enumerating 1000 LinkedIn search pages for Trustwave employees.

<pre>
$ python LinkedInUserEnum.py 21523 1000
 ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____
||L |||i |||n |||k |||e |||d |||I |||n |||E |||n |||u |||m ||
||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|
LinkedIn Username: lvonniebelschuetz-godlewski@trustwave.com
LinkedIn Password:
[!] Authenticating...
[!] Authentication for "lvonniebelschuetz-godlewski@trustwave.com" succeeded!
[!] Enumerating page number 1 for users...
[!] Enumerating page number 2 for users...
[!] Enumerating page number 3 for users...
<i>...TRUNCATED...</i>
[!] Enumerating page number 99 for users...
[!] Enumerating page number 100 for users...
[!] Enumerating page number 101 for users...
[!] No more matches found...
[!] User enumeration complete!
[!] 983 LinkedIn users were enumerated! First name, last name and title was written to "/TW-Tools/Scripts/Recon/21523_linkedin_users.csv"!
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
[!] 983 usernames written to "/TW-Tools/Scripts/Recon/21523_usernames.txt"!
</pre>
