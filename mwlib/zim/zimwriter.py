#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.


def writer(env, output,
           status_callback=None,
           ):
    print 'writing!'

writer.description = 'ZIM Files'
writer.content_type = 'application/zim' # FIXME: verify/correct
writer.file_extension = 'zim'
