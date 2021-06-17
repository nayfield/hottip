#!/usr/bin/env python

import os
import configparser

def remove_unknowns():
    ''' Remove dead torrents '''
    pass


def get_tors():
    ''' return json of minimal client state'''
    pass

def tagusage(torl, tag=None):
    ''' report GB (/1024) usage of all torrents '''

def tags_by_overage(torl, tagl):
    ''' return a list of (tag, over) sorted by amount over
        tagl[tag] = targetusage'''

def get_culls(torl, tag, holdt, over):
    ''' return oldest items in torlist,
         matching tag,
         seeded over holdt,
         not exceeding over
         return tuple ([hashes], size)'''
    pass

def do_culls(culll):
    ''' cull a list of hashes'''

def save_state(fn, struc):
    ''' pickle struc to fn'''

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
    boxused = tagusage(torlist)
    boxused = 10
    over = boxused - boxmax

    if over > 0:
        culls = []
        tgtleft = over

        ttgts = {}
        for x in conf.sections():
            ttgts[x] = conf[x].get('tgt')

        tags = tags_by_overage(torlist, ttgs)
        for tagd in tags:
            if tgtleft <= 0:
                continue
            tag, over = tagd
            holdt = conf[tag].get('hold')
            hashs, tsize = get_culls(torlist, tag, holdt, over)
            culls.extend(hashs)
            tgtleft -= tsize

        if tgtleft < 0:
            # now we fifo everything
            hashs, tsize = get_culls(torlist, None, 1, tgtleft)
            tgtleft -= tsize
            culls.extend(hashs)
        # could add another panic here if still have tgtleft

        do_culls(hashs)

        # Since we culled, grab a new torlist
        torlist = get_tors()

    save_state(stfile, torlist)
