#!/usr/bin/env PATH=$PATH:/usr/local/bin python3

from __future__ import print_function

from alfred import AlfredHelper

if __name__ == '__main__':
    alfred = AlfredHelper()
    alfred.output_regions()
