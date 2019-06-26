import github3, os, git, shutil, tempfile, getpass, sharepy, sys, json, time, logging

repocount = 0
readmecount = 0
folderpath = str(os.path.realpath(__file__))[:-16]
fastmode = False
SPUrl = "zimbaniptyltd.sharepoint.com"
libraryName = "Shared%20Documents"
logging.basicConfig(filename="UploadedFiles.log",
                    level=logging.INFO,
                   	format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
path = folderpath

def uploadToSharepoint(SPUrl, libraryName, FolderPath):
    if os.path.isfile("sp-session.pkl"):
    	s = sharepy.load(fastmode)
    else:
    	s = sharepy.connect(SPUrl)
    	s.save()
    if os.name == 'nt':
        folder = FolderPath.split('\\')
    else:
        folder = FolderPath.split('/')
 
    if os.path.isdir(FolderPath):
 
        p = s.post("https://"+SPUrl+"/_api/web/folders",
        json={
            "__metadata": { "type": "SP.Folder" },
            "ServerRelativeUrl": libraryName +'/' + folder[-2]
            })
             
        logging.info("Created Folder %s: with response %s", folder, p.content)
 
        filesToUpload = os.listdir(FolderPath)
         
        for fileToUpload in filesToUpload:
            headers = {"accept": "application/json;odata=verbose",
            "content-type": "application/x-www-urlencoded; charset=UTF-8"}
             
            with open(os.path.join(FolderPath, fileToUpload), 'rb') as read_file:
                content = read_file.read()
             
            p = s.post(f"https://{SPUrl}/_api/web/GetFolderByServerRelativeUrl('{libraryName}/{folder[-2]}')/Files/add(url='{fileToUpload}',overwrite=true)", data=content, headers=headers)
             
            logging.info("Uploaded %s: with response %s", folder, p.content)

if len(sys.argv) > 1:
	if sys.argv[1] == '-f':
		fastmode = True

if not fastmode:
	print("\nWARNING: This program will remove all files in the folder it is in, except for itself, sp-session.pkl, and readmecount.md")
	l = input("\nWould you like to see a list of these files? (y/n): ")
	if l.lower() == 'y':
		print()
		for file in os.listdir(folderpath):
			if (file != "readme-puller.py") and (file != "sp-session.pkl") and (file != "readmecount.md"):
				print(str(file))
	else:
		print("    Skipping...")	

	i = input("\nDo you want to continue? (y/n): ")
	if i.lower() == 'n':
		sys.exit()
	elif (i.lower() != 'y') and (i.lower() != 'n'):
		print("You did not enter 'y' or 'n'. The program is terminating for safety.")
		sys.exit()

	print()
	guser = input("Enter your GitHub username: ")
	gpw = getpass.getpass("Enter the password for '" + guser + "@github': ")
	print()

if fastmode:
	f = open(sys.argv[2], "r")
	guser = f.readline()[:-1]
	gpw = f.readline()
	f.close()

gh = github3.login(guser, gpw)
org = gh.organization("Zimbani")
repos = list(org.repositories(type="all"))

for file in os.listdir(folderpath):
	if (file != "readme-puller.py") and (file != "sp-session.pkl") and (file != "readmecount.md"):
		os.remove(folderpath + file)

for repo in repos:
	url = "git@github.com:" + str(repo) + ".git"
	if not fastmode:
		print("Checking for README in: " + url[23:-4])

	t = tempfile.mkdtemp()
	git.Repo.clone_from(url, t, branch='master', depth=1)
	fpath = 'notarealfile.xyz'
	
	if os.path.exists(t + '/README.md'):
		fpath = str(repo)[8:] + "_README.md"
		shutil.move(os.path.join(t, 'README.md'), folderpath + fpath)
		if not fastmode:
			print("    Successfully downloaded README file as " + fpath)

		readmecount += 1
	elif os.path.exists(t + '/README.txt'):
		fpath = str(repo)[8:] + "_README.txt"
		shutil.move(os.path.join(t, 'README.txt'), folderpath + fpath)
		if not fastmode:
			print("    Successfully downloaded README file as " + fpath)

		readmecount += 1
	else:
		if not fastmode:
			print("    This repository has no README file!")

	repocount += 1
	shutil.rmtree(t)

if not fastmode:
	print("\nLogging in to SharePoint (first.last@zimbani.com) to upload README files...\n")

uploadToSharepoint(SPUrl, libraryName, path)

if not fastmode:
	print("\nSuccess! All README files pulled from GitHub and uploaded to SharePoint!")

	print("NOTE: " + str(readmecount) + "/" + str(repocount) + " repositories contain a README file.")

if fastmode:
	f = open(folderpath + "log.md", "w+")
	f.write(str(readmecount) + "/" + str(repocount) + "\n")
	f.close()

f = open(folderpath + "readmecount.md", "r+")
line = f.readline()
f.close()
if line == '':
	f = open(folderpath + "readmecount.md", "w")
	f.write(str(readmecount))
	f.close()
f = open(folderpath + "readmecount.md", "r+")
diff = readmecount - int(f.readline())
if not fastmode:
	print("This is " + str(diff) + " more than the last time this script was run.\n")

if fastmode:
	f = open(folderpath + "log.md", "a")
	f.write("This is " + str(diff) + " more than the last time this script was run.")
	f.close()

f.close()
f = open(folderpath + "readmecount.md", "w")
f.write(str(readmecount))
f.close()