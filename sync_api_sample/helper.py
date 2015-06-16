#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys

SYNC_API_BASE_URL = 'http://localhost:8888/api/v2'

# Update with path to folders
SYNC_FOLDER_PATH = '/Users/kaelar/Desktop/Sync test'
STATUS_FOLDER_PATH = '/Users/kaelar/Desktop/Status'

EVENTS_LIST = [
    # 'EVENT_LOCAL_FILE_ADDED',
    # 'EVENT_REMOTE_FILE_ADDED',
    'EVENT_LOCAL_FILE_REMOVED',
    'EVENT_REMOTE_FILE_REMOVED',
    # 'EVENT_LOCAL_FILE_CHANGED',
    # 'EVENT_REMOTE_FILE_CHANGED',
    'EVENT_FILE_DOWNLOAD_COMPLETED',
]

def setup_folders():
    res = requests.post('%s/folders?path=%s' % (SYNC_API_BASE_URL, SYNC_FOLDER_PATH))
    if res.status_code != 201:
        print 'Unable to add sync folder. Verify the path is correct and the folder ' \
              'has not already been added.'
        return
    sync_folder_share_id = res.json().get('data').get('shareid')

    res = requests.post('%s/folders?path=%s' % (SYNC_API_BASE_URL, STATUS_FOLDER_PATH))
    if res.status_code != 201:
        print 'Unable to add status folder. Verify the path is correct and the folder ' \
              'has not already been added.'
        return
    status_folder_share_id = res.json().get('data').get('shareid')

    data = {
        'sync': sync_folder_share_id,
        'status': status_folder_share_id
    }
    with open('%s/config.txt' % STATUS_FOLDER_PATH, 'w') as config_file:
        config_file.write(json.dumps(data))
        print 'Writing to config file >>> '


def get_folder_path(folder):
    res = requests.get('%s/folders/%s' % (SYNC_API_BASE_URL, folder))
    path = res.json().get('data').get('path')

    # Windows path wierdness, don't understand this yet...
    if path.startswith('\\\\?\\'):
        path = path[4:]
    return path


def find_folder_id(share_id):
    '''
    find a folder id based on share id. Share id is a unique identifier for a folder.
    Folder id is different across different users

    '''
    res = requests.get('%s/folders' % SYNC_API_BASE_URL)
    folders = res.json().get('data').get('folders')
    for folder in folders:
        if folder.get('shareid') == share_id:
            return folder.get('id')
    return None


def check_peer_status():
    with open('%s/config.txt' % STATUS_FOLDER_PATH, 'r') as  config_file:
        data = json.loads(config_file.read())
        status_folder_id = find_folder_id(data.get('status'))
        sync_folder_id = find_folder_id(data.get('sync'))

    # Get path of folder that contains peer status files
    status_folder_path = get_folder_path(status_folder_id)

    # Get folder hash of the folder you want to keep in sync
    res = requests.get('%s/folders/%s/activity' % (SYNC_API_BASE_URL, sync_folder_id))
    client_hash = res.json().get('data').get('hash')

    # Get peers of folder so we can check if they are in sync
    peers = res.json().get('data').get('peers')

    # Loop through peers, reading status file for each to compare hash values.
    # Status file is named by peer id. Hash value will match main client's folder hash
    # if the two folders are in the same sync state
    peer_list = []
    for peer in peers:
        try:
            _id = peer.get('id')
            with open('%s/%s.txt' % (status_folder_path, _id), 'r') as status_file:
                data = json.loads(status_file.read())
                is_online = peer.get('isonline')

                # Convert time ticks to display str
                data['last_modified'] = time.ctime(int(data['last_modified']))
                data['peer_id'] = _id
                data['is_online'] = 1 if is_online else 0
                data['sync'] = 1 if data['hash'] == client_hash else 0
                peer_list.append(data)
        except IOError:
            unknown_peer = {}
            unknown_peer['name'] = 'Unknown'
            unknown_peer['peer_id'] = _id
            unknown_peer['last_modified'] = 'Unknown'
            unknown_peer['is_online'] = -1
            unknown_peer['sync'] = -1
            peer_list.append(unknown_peer)
    return peer_list


def update_peer_status():
    last_event_id = -1

    # Load config file that stores folder share ids. Use share id to find
    # folder id
    with open('%s/config.txt' % STATUS_FOLDER_PATH, 'r') as  config_file:
        data = json.loads(config_file.read())
        sync_folder_share_id = data.get('sync')
        sync_folder_id = find_folder_id(sync_folder_share_id)
        status_folder_id = find_folder_id(data.get('status'))

    # Get path of folder that contains peer status files
    status_folder_path = get_folder_path(status_folder_id)

    # Get peer id
    res = requests.get('%s/client' % SYNC_API_BASE_URL)
    peer_id = res.json().get('data').get('peerid')

    # Get peer name
    res = requests.get('%s/client/settings' % SYNC_API_BASE_URL)
    peer_name = res.json().get('data').get('devicename')

    # Should update status once on start
    write_peer_status(peer_id, peer_name, status_folder_path, sync_folder_id)

    while True:
        try:
            print 'Request with Event ID >> %s' % last_event_id #DEBUG
            res = requests.get('%s/events?id=%s' % (SYNC_API_BASE_URL, last_event_id))
            events = res.json().get('data').get('events')

            # Sort events by id. We want lowest id (earliest) events first so they process first
            # By default we are returned highest id (most current) events
            sorted_events = sorted(events, key=lambda k: k['id'], reverse=False)

            for event in sorted_events:
                event_type = event.get('typename')
                event_id = event.get('id')

                # Set highest event id (most recent event) to last_event_id so we don't get duplicates
                if event_id > last_event_id:
                    last_event_id = event_id

                # We only care about folder events where the state changes
                if event_type not in EVENTS_LIST:
                    continue
                else:
                    # We do this here because not all events have a folder object
                    share_id = event.get('folder').get('shareid')

                    # We only care about events for the folder that we want to keep in sync
                    if share_id != sync_folder_share_id:
                        continue

                    write_peer_status(peer_id, peer_name, status_folder_path, sync_folder_id)
        except Exception as e:
            print 'Error %s' % e
            # pass


def write_peer_status(peer_id, peer_name, status_folder_path, sync_folder_id):
    # Get hash of folder you want to keep in sync
    res = requests.get('%s/folders/%s/activity' % (SYNC_API_BASE_URL, sync_folder_id))
    _hash = res.json().get('data').get('hash')

    # Create json object to write to file
    data = {}
    data['name'] = peer_name
    data['last_modified'] = time.time()
    data['hash'] = _hash

    with open('%s/%s.txt' % (status_folder_path, peer_id), 'w') as status_file:
        status_file.write(json.dumps(data))
        print 'Writing to status file >>> Peer id: ' + peer_id


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Error, missing arguments'
        sys.exit()
    if sys.argv[1] == '--setup':
        setup_folders()
    elif sys.argv[1] == '--peer':
        update_peer_status()
    else:
        print 'Error, invalid argument'
