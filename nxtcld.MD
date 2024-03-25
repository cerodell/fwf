# Using rclone with NextCloud
## Configure rclone for NextCloud
### Open a terminal
- run `rclone config`
- Select new remote and name it nextcloud (or whatever youd like)
``````
 $  rclone config

Current remotes:
Name                 Type
====                 ====
mydrive              drive
sfire                    drive
shared               drive
e) Edit existing remote
n) New remote
d) Delete remote
r) Rename remote
c) Copy remote
s) Set configuration password
q) Quit config
e/n/d/r/c/s/q> n
name> nextcloud
``````

### Webdav Storage type
- Select `XX / Webdav`
- For more [information](https://rclone.org/webdav/)

``````
Type of storage to configure.
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value
 1 / 1Fichier
   \ "fichier"
 2 / Alias for an existing remote
   \ "alias"
 3 / Amazon Drive
   \ "amazon cloud drive"
 4 / Amazon S3 Compliant Storage Provider (AWS, Alibaba, Ceph, Digital Ocean, Dreamhost, IBM COS, Minio, etc)
   \ "s3"
 5 / Backblaze B2
   \ "b2"
 6 / Box
   \ "box"
 7 / Cache a remote
   \ "cache"
 8 / Dropbox
   \ "dropbox"
 9 / Encrypt/Decrypt a remote
   \ "crypt"
10 / FTP Connection
   \ "ftp"
11 / Google Cloud Storage (this is not Google Drive)
   \ "google cloud storage"
12 / Google Drive
   \ "drive"
13 / Google Photos
   \ "google photos"
14 / Hubic
   \ "hubic"
15 / JottaCloud
   \ "jottacloud"
16 / Koofr
   \ "koofr"
17 / Local Disk
   \ "local"
18 / Mega
   \ "mega"
19 / Microsoft Azure Blob Storage
   \ "azureblob"
20 / Microsoft OneDrive
   \ "onedrive"
21 / OpenDrive
   \ "opendrive"
22 / Openstack Swift (Rackspace Cloud Files, Memset Memstore, OVH)
   \ "swift"
23 / Pcloud
   \ "pcloud"
24 / Put.io
   \ "putio"
25 / QingCloud Object Storage
   \ "qingstor"
26 / SSH/SFTP Connection
   \ "sftp"
27 / Union merges the contents of several remotes
   \ "union"
28 / Webdav
   \ "webdav"
29 / Yandex Disk
   \ "yandex"
30 / http Connection
   \ "http"
31 / premiumize.me
   \ "premiumizeme"
Storage> 28

``````
### URL
- use `https://wfrt-nc.eoas.ubc.ca/remote.php/webdav` as url
``````
** See help for webdav backend at: https://rclone.org/webdav/ **
URL of http host to connect to
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value
 1 / Connect to example.com
   \ "https://example.com"
url> https://wfrt-nc.eoas.ubc.ca/remote.php/webdav

``````
### Vendor option
- choose ` XX / Nextcloud`
``````
Name of the Webdav site/service/software you are using
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value
 1 / Nextcloud
   \ "nextcloud"
 2 / Owncloud
   \ "owncloud"
 3 / Sharepoint
   \ "sharepoint"
 4 / Other site/service or software
   \ "other"
vendor> 1

``````
### Enter user name
- this is your username on nextcloud that Henryk gave you
``````
User name
Enter a string value. Press Enter for the default ("").
user> <YOUR USER NAME>

``````
### Enter user pwd
- select `y) Yes type in my own password`
- Enter your pwd for nextcloud

``````
Password.
y) Yes type in my own password
g) Generate random password
n) No leave this optional password blank
y/g/n> y
Enter the password:
password: <YOUR USER PWD>
Confirm the password:
password: <YOUR USER PWD>

``````
### Bearer token
- Leave Bearer token token blank by hitting enter
``````
Bearer token instead of user/pass (eg a Macaroon)
Enter a string value. Press Enter for the default ("").
bearer_token>

``````
### advanced config
- select `n`
``````
Edit advanced config? (y/n)
y) Yes
n) No
y/n> n

``````

### Confirm config
- confirm you configuration and selcet `y` if correct

``````
Remote config
--------------------
[nextcloud]
type = webdav
url = https://wfrt-nc.eoas.ubc.ca/remote.php/webdav
vendor = nextcloud
user = crodell
pass = *** ENCRYPTED ***
--------------------
y) Yes this is OK
e) Edit this remote
d) Delete this remote
y/e/d> y
Current remotes:
Name                 Type
====                 ====
mydrive              drive
nextcloud            webdav
sfire                drive
shared               drive
e) Edit existing remote
n) New remote
d) Delete remote
r) Rename remote
c) Copy remote
s) Set configuration password
q) Quit config
e/n/d/r/c/s/q>
``````

## Transfer data to next cloud with rclone
- - For more [information](https://rclone.org/commands/rclone_copy/)
``````
rclone copy -v /path/to/source/directory nextcloud:/path/to/destination/directory
``````
