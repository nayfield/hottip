#!/usr/bin/env python

import os
import configparser
import subprocess
import json
import pickle
import time


def scmd(st):
    retval = []
    remote = False
    if remote:
        retval = ['ssh', remote]
    retval.extend(st)
    return retval


def remove_unknowns():
    """ Remove dead torrents """
    rcmd = ['rtcontrol', '-q', '-ohash', 'message=*Unregistered*', '--cull', '--yes']
    retval = subprocess.call(scmd(rcmd))

    return retval


# TODO match transmission
def get_tors():
    """ return json of minimal client state"""
    fields = ['hash', 'custom_getter', 'size', 'seedtime', 'alias', 'message', 'name', 'completed']
    # Some extra stuff might not be needed
    fields.extend(['custom_1', 'uploaded', 'is_complete', 'is_open', 'started', 'custom_tm_uploaded'])
    # rtxml equiv
    # rtxmlrpc --repr d.multicall2 '' '' d.hash= d.custom=getter d.size_bytes= d.message= d.name= d.timestamp.finished=
    # can't get alias.
    # workaround - after getting other vars, including d.custom=alias:
    #   per empty alias= entries, call rtxmlrpc --repr t.multicall <hash> '' t.url= ... to get url, parse, store.
    rcmd = ["rtcontrol", '-q', '--json', '*', '-o' + ','.join(fields)]
    cout = subprocess.check_output(scmd(rcmd))

    # TODO custom_getter references are deprecated

    # onetag = non-overlapping tags
    retval = []
    for t in json.loads(cout):
        if not t['is_complete']:
            continue
        if t['custom_getter']:
            t['onetag'] = t['custom_getter']
        elif t['custom_1']:
            t['onetag'] = t['custom_1']
        else:
            t['onetag'] = 'Alias:' + t['alias']
        retval.append(t)
    return retval

