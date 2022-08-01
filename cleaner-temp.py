#!/usr/bin/env python

import os
import configparser
import subprocess
import json
import pickle
import time
import hottip.client_trans

# TODO - switch from config to use client_rtcontrol or client_trans.
# TODO - move more logic to common


def save_state(fn, struc):
    """ pickle struc to fn"""
    # this is for other things to look at TODO
    # TODO write out to a tmp file then move into place
    # in order to transact atomically
    with open(fn, 'wb') as output:
        pickle.dump(struc, output, 4)


if __name__ == '__main__':
    # TODO use python-daemon?

    mydir = os.path.expanduser('~/.hottip')
    myconfig = os.path.join(mydir, 'cleaner.cfg')
    stfile = os.path.join(mydir, 'torlist-tr.pk')
    conf = configparser.ConfigParser()
    conf.read(myconfig)

#    remove_unknowns()
    client = hottip.client_trans.open_client(conf['DEFAULT'].get('truser'), conf['DEFAULT'].get('trpass'))
    torlist = hottip.client_trans.get_tors(client)


    save_state(stfile, torlist)
