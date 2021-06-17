#!/usr/bin/env python

import os
import configparser
import subprocess
import json
import pickle


def remove_unknowns():
    ''' Remove dead torrents '''
    rcmd = 'rtcontrol -q -o hash message="*Unregistered*"  --cull --yes'
    scmd = [rcmd]
    retval = subprocess.call(scmd)

    return retval


def get_tors():
    ''' return json of minimal client state'''
    fields = ['hash', 'custom_getter', 'size', 'seedtime', 'alias', 'message']

    rcmd = "rtcontrol -q --json \* -o"+",".join(fields)
    scmd = [rcmd]
    cout = subprocess.check_output(scmd)

    return json.loads(cout)

def filterlist(torl, tag):
    if not tag:
        return torl
    retval = []
    al = None
    if tag.startswith('Alias'):
        al = tag.split(':')[1]
    for t in torl:
        if al:
            if t['alias'] == al:
                retval.append(t)
        elif t['custom_getter'] == tag:
                retval.append(t)
    return retval

def tagusage(torl, tag):
    ''' report GB (/1024) usage of all torrents '''
    retval = 0
    for t in filterlist(torl, tag):
        retval += t['size']
    return int(retval/1024/1024/1024)

def tags_by_overage(torl, tagl):
    ''' return a list of (tag, over) sorted by amount over
        input tagl[tag] = targetusage'''
    overd = {}
    for t in tagl.keys():
        overd[t] = tagusage(torl, t) - int(tagl[t])

    retval = []
    for i in sorted(overd.keys(), key=lambda x: x[1], reverse=True):
        retval.append((i, overd[i]))
    return retval



def get_culls(torl, tag, holdt, goal):
    ''' return oldest items in torlist,
         matching tag,
         seeded over holdt,
         not exceeding over
         return tuple ([hashes], size)'''
    fl = filterlist(torl, tag)
    tl = sorted(fl, key=lambda k: k['seedtime'], reverse=True)
    culled = 0
    hashlist = []
    for t in tl:
        if culled > goal:
            continue
        if t['seedtime'] < holdt*60*60*24:
            hashlist.append(t['hash'])
            culled += t['size']/1024/1024/1024

    return hashlist, culled




def do_culls(culll):
    ''' cull a list of hashes'''
    rcmd = "rtcontrol hash="+','.join(culll)+" --cull --yes"
    scmd = [rcmd]
    retval = subprocess.call(scmd)
    return retval

def save_state(fn, struc):
    ''' pickle struc to fn'''
    # this is for other things to look at TODO
    # TODO write out to a tmp file then move into place
    # in order to transact atomically
    with open(fn, 'wb') as output:
        pickle.dump(struc, output, -1)


if __name__ == '__main__':
    #TODO use python-daemon?

    mydir=os.path.expanduser('~/.hottip')
    myconfig=os.path.join(mydir, 'cleaner.cfg')
    stfile=os.path.join(mydir, 'torlist.pk')
    conf=configparser.ConfigParser()
    conf.read(myconfig)

    remove_unknowns()
    torlist = get_tors()

    boxmax = int(conf['DEFAULT'].get('max'))
    boxmax = 2649
    boxused = tagusage(torlist, None)
    over = boxused - boxmax

    if over > 0:
        culls = []
        tgtleft = over

        ttgs = {}
        for x in conf.sections():
            ttgs[x] = conf[x].get('tgt')

        tags = tags_by_overage(torlist, ttgs)
        for tagd in tags:
            if tgtleft <= 0:
                continue
            tag, tover = tagd
            holdt = conf[tag].get('hold')
            hashs, tsize = get_culls(torlist, tag, holdt, tover)
            culls.extend(hashs)
            tgtleft -= tsize

        if tgtleft > 0:
            # now we fifo everything
            hashs, tsize = get_culls(torlist, None, 1, tgtleft)
            tgtleft -= tsize
            culls.extend(hashs)
        # could add another panic here if still have tgtleft

        do_culls(hashs)

        # Since we culled, grab a new torlist
        torlist = get_tors()

    save_state(stfile, torlist)
