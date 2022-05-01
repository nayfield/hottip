#!/usr/bin/env python3



import transmission_rpc
from urllib.parse import urlparse

def open_client(u, p, host="127.0.0.1", port=9091, path="/transmission/", proto="http"):
    """
    Open a connection to transmission and return handle
    """

    return(transmission_rpc.Client(username=u, password=p, host=host, port=port, path=path, protocol=proto))

def get_tors(c):
    """
    Returns client torrents as list of dicts

    Fields include:
    . id (int)
    . hash
    . name
    . status
    . fin (bool)
    . size (bytes)
    . labels (list of labels)
    . label (first label)
    . err (tracker error string)
    . timestamps: donets, actts

    """

    retval=[]

    for t in c.get_torrents():
        rec={}

        rec["id"]       = t.id
        rec["hash"]     = t.hashString
        rec["name"]     = t.name
        rec["status"]   = t.status
        rec["fin"]      = t.is_finished
        rec['size']     = t.sizeWhenDone
        rec["labels"]   = t.labels
        rec["label"]    = t.labels[0]
        rec["err"]      = t.errorString
        rec["donets"]   = t.doneDate
        rec["actts"]    = t.activityDate
        rec["tracker"]  = urlparse(t.trackers[0]['announce']).hostname

        retval.append(rec)

    return(retval)



def add_torrent(c, url, tag=None):
    """
    Add a torrent by URL
    """

    ret = c.add_torrent(url)

    if tag:
        c.change_torrent(ret, tag)

    return ret.id


def remove_torrent(c, id, delete_data=True):
    """
    Remove a torrent by ID
    """

    c.remove_torrent(id, delete_data)
    