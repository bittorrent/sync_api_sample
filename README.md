# BitTorrent Sync API v2 Tutorial

### Install BitTorrent Sync
Install a version of BitTorrent Sync that includes API v2 support. You can get it [HERE] ...blahblah

### Request API Key
Contact BitTorrent support to request an API key. [HERE] .....blahblah

### Create configuration file
Create a file named sync.conf and copy the code below. Place it in the following folder.

OSX: ~/Library/Application Support/BitTorrent Sync/sync.conf

Windows: C:\Users\username\AppData\Roaming\BitTorrent Sync\sync.conf
```
sync.conf
{
  "device_name": "My Sync System",
  "use_gui": true,
  "pid_file": "sync.pid",
  "webui": {
    "api_key": [YOUR_API_KEY],
     "listen": "0.0.0.0:8888"
  }
}
```

Start up BitTorrent Sync client and you are ready to go.

### API commands
Lets test some API commands. First, we can add a local folder to sync. There are multiple ways you can pass in data. For the examples, I will be adding a folder of books I want to share.
```
POST /folders
```

Using query string parameters:
```sh
$ curl -X POST http://localhost:8888/api/v2/folders\?path=/Users/me/Desktop/books
```

Using json data:
```sh
$ curl -X POST -H "Content-Type: application/json" -d '{"path": "/Users/me/Desktop/books"}' http://localhost:8888/api/v2/folders
```

Using x-www-form-urlencoded form-data
```sh
$ curl -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d "path=/Users/me/Desktop/books"  http://localhost:8888/api/v2/folders
```

You should get a response in the following format:
```json
{
  "data": {
    "date_added": 1432857089,
    "deletetotrash": true,
    "id": "123",
    "ismanaged": true,
    "iswritable": true,
    "name": "books",
    "path": "test_folder",
    "paused": false,
    "relay": true,
    "searchdht": false,
    "searchlan": true,
    "shareid": "12345asdf12354",
    "stopped": false,
    "synclevel": 2,
    "synclevelname":
    "full sync",
    "usehosts": false,
    "usetracker": true
  },
  "method": "POST",
  "path": "/api/v2/folders",
  "status": 0
}
```

Now we have added a folder to sync. If you open the client, you should see the folder show up. You can also check what folders you have using the api.

```sh
$ curl -X GET http://localhost:8888/api/v2/folders
```

Response:
```json
{
  "data": {
    "folders": [
      {
        "date_added": 1432923595,
        "deletetotrash": true,
        "id": "123",
        "ismanaged": true,
        "iswritable": true,
        "name": "books",
        "path": "/Users/me/Desktop/books",
        "paused": false,
        "relay": true,
        "searchdht": false,
        "searchlan": true,
        "shareid": "12345asdf12354",
        "stopped": false,
        "synclevel": 2,
        "synclevelname": "full sync",
        "usehosts": false,
        "usetracker": true
      }
    ]
  },
  "method": "GET",
  "path": "/api/v2/folders",
  "status": 0
}
```

Now lets share the folder by creating a link. We will set a few parameters:

timelimit: 3600 - Link will be valid for 3600 seconds (1 hour)

askapproval: 0 - Peers are automatically approved to access folder

permissions: 2 - Peers will only get read only access to the folder

```sh
$ curl -X POST -H 'Content-Type: application/json' -d '{"timelimit": "60", "askapproval": 0, "permissions": 2}' http://localhost:8888/api/v2/folders/123/link
```

Response:
```json
{
  "data": {
    "link": "https://link.getsync.com/#f=books&sz=43E6&t=LAGW4AX5AVW4GUO3SL27890&v=2.1"
  },
  "method": "POST",
  "path": "/api/v2/folders/123/link",
  "status": 0
}
```

Send the link to another device or a friend that is using Sync and you are on your way to syncing a folder.

# Sample Application
Suppose we have a fire station with x number of fire trucks. The fire station will share a folder with all the fire trucks that will contain information to help them stay up to date. The fire station wants to constantly know if each fire truck is in sync and has recieved the new files in the folder. This sample application will help us accomplish this scenario.

### Setup folders
The BitTorrent Sync client needs to be installed on all systems (fire station and fire trucks). Using the BitTorrent Sync client on the main client (fire station) , add the folder you want to keep in sync. We will call this the Sync folder. Also, we need to add a second folder. This folder can be located anywhere and we will call it the Status folder. We now need to share these folders with all the peers (fire trucks). The Sync folder can be read only. The Status folder needs to have read/write permissions.

The Status folder is needed to keep the hash state of the Sync folder for each peer. We use this folder hash to check if a folder is in sync. We do this because we assume fire trucks will be driving around and in and out of connectivity and may not always be able to communicate directly with the main client. Storing the most recent state of each peer in this Status folder will allow the main client to always have access to the latest state of each peer.

### Getting folder share id
We need to get the folder share id for the Sync and Status folders
```sh
$ curl -X GET http://localhost:8888/api/v2/folders
```
```json
{
  "data": {
    "folders": [
      {
        "date_added": 1432923595,
        "deletetotrash": true,
        "id": "123",
        "ismanaged": true,
        "iswritable": true,
        "name": "Sync",
        "path": "/Users/me/Desktop/Sync",
        "paused": false,
        "relay": true,
        "searchdht": false,
        "searchlan": true,
        "shareid": "12345asdf12354",
        "stopped": false,
        "synclevel": 2,
        "synclevelname": "full sync",
        "usehosts": false,
        "usetracker": true
      },
      {
        "date_added": 1432923595,
        "deletetotrash": true,
        "id": "124",
        "ismanaged": true,
        "iswritable": true,
        "name": "Status",
        "path": "/Users/me/Desktop/Status",
        "paused": false,
        "relay": true,
        "searchdht": false,
        "searchlan": true,
        "shareid": "12345asdf12354a",
        "stopped": false,
        "synclevel": 2,
        "synclevelname": "full sync",
        "usehosts": false,
        "usetracker": true
      },      
    ]
  },
  "method": "GET",
  "path": "/api/v2/folders",
  "status": 0
}
```
Get the shareid for the Sync and Status folders and copy them into the sync_api_sample/helper.py file into the variables SYNC_FOLDER_SHARE_ID and STATUS_FOLDER_SHARE_ID.

### Setup peers
Along with having BitTorrent Sync installed, each peer(fire truck) needs to run a helper script located at sync_api_sample/helper.py.
```sh
$ python sync_api_sample/helper.py --peer
```
This runs a script that will listen to BitTorrent Sync events, and on specific folder change events, will update the Status folder with an updated text file containing its current hash of the Sync folder along with some other information. It will name the file based on its peer id.

### Setup main client
The main client (fire station) needs to run the following
```sh
$ sudo python runserver.py
```
Now open your webbrowser and go to 'http://127.0.0.1/'. There you should see a Sync Dashboard that displays the sync state of each peer. It gets this information by pulling the peer text files in the Status folder and checking the hash value in those files and comparing them with its current hash value on the Sync Folder.

![Sync Dashboard](https://github.com/bittorrent/sync_api_sample/blob/master/Dashboard%20Sample.png)

