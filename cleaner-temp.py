#!/usr/bin/env python

import os
import configparser

import hottip.client_trans
import hottip.common

# TODO - switch from config to use client_rtcontrol or client_trans.
# TODO - move more logic to common



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


    hottip.common.save_state(stfile, torlist)
