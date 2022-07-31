#!/usr/bin/env python

import os
import configparser
import subprocess
import json
import pickle
import time
import client_trans



def filterlist(torl, ftag):
    if not ftag:
        return torl
    retval = []
    for t in torl:
        if t['onetag'] == ftag:
            retval.append(t)
    return retval


def tagusage(torl, utag):
    """ report GB (/1024) usage of all torrents """
    retval = 0
    for t in filterlist(torl, utag):
        retval += t['size']
    return int(retval / 1024 / 1024 / 1024)


def tags_by_overage(torl, tagl):
    """ return a list of (tag, over) sorted by amount over
        input tagl[tag] = targetusage"""
    overd = {}
    for t in tagl.keys():
        overt = tagusage(torl, t) - int(tagl[t])
        if overt > 0:
            overd[t] = overt
    return sorted(overd.items(), key=lambda k: k[1], reverse=True)


# TODO refactor
def get_culls(torl, ctag, choldt, goal, exempt=None):
    """ return oldest items in torlist,
         matching tag,
         seeded over holdt,
         not exceeding over
         return tuple ([hashes], size)"""
    fl = filterlist(torl, ctag)
    tl = sorted(fl, key=lambda k: k['completed'])
    culled = 0
    cutoff = int(time.time())
    cutoff -= choldt * 60 * 60
    hashlist = []
    for t in tl:
        if culled > goal:
            continue
        if exempt:
            if t['onetag'] in exempt.split(','):
                continue
        if t['completed'] < cutoff:
            hashlist.append(t['hash'])
            culled += t['size'] / 1024 / 1024 / 1024

    return hashlist, culled


def save_state(mys, struc):
    """ pickle write struc to mys"""
    # this is for other things to look at TODO
    # TODO write out to a tmp file then move into place
    # in order to transact atomically
    with open(fn, 'wb') as output:
        pickle.dump(struc, output, 4)

def load_state(mys):
    """
    Load pickle from mys - return empty dict
    if it doesn't exist
    """
    retval={}
    if os.path.isfile(mys):
        with open(mys, 'rb') as readin:
            retval=pickle.load(readin)
    return retval

def update_history(mystate, torl, interval=7, maxintv=10):
    """
    Given a state dict and torlist,
    return updated state dict based on torlist
    returns a hash-indexed dict of upload bytes by date

    interval = days interval
    max = max # of intervals (all greater than interval*max in same bucket)
    """
    
    now=int(time.time())

    retval={}

    for t in torl:
        if t['status'] != 'seeding':
            continue

        if t['hash'] in mystate:
            retval[t['hash']] = mystate[t['hash']]
        else:
            retval[t['hash']] = dict()

        intv = (now - t['donets']) // (interval * 60 * 60 * 24)
        if intv > maxintv:
            intv = maxintv
        retval[t['hash']][intv] = t['up']

    return retval
            
        
def record_history(mys, client):
    """
    update the history state at file mys given a client handle
    """

    tors = client_trans.get_tors(client)
    oldstate = load_state(mys)
    newstate = update_history(oldstate, tors)
    save_state(newstate)




