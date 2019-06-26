from requests_html import HTMLSession, sys
lines, i = HTMLSession().get("https://api.github.com/users/" + sys.argv[1] + "/events/public").text.split("\n"), -1
for x in range(4):
	for i in range(max(x, i), len(lines)):
		if ["payload", "commits", "author", sys.argv[2]][x] in lines[i]: break		
print("\n" + sys.argv[2] + ": " + lines[i][lines[i].find(sys.argv[2]) + len(sys.argv[2]) + 4:-(len(sys.argv[2]) - 3)] + "\n")
