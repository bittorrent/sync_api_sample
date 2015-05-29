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
$ curl -X GET -H http://localhost:8888/api/v2/folders
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


