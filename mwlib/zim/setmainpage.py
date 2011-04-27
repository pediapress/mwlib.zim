#! /usr/bin/env python
#! -*- coding:utf-8 -*-

import struct

def read_int(f, pos, length):
    f.seek(pos)
    val = f.read(length)
    if length == 4:
        fmt = 'L'
    elif length == 8:
        fmt = 'Q'
    return struct.unpack('<%s' % fmt, val)[0]

def read_str(f, pos):
    f.seek(pos)
    res = []
    val = None
    while val != '\0':
        val = f.read(1)
        res.append(val)
    res = res[:-1]
    return ''.join(res)

def walk_url_pointers(f, pos, n):
    for offset in range(n):
        dir_entry = read_int(f, pos+offset*8, 8)
        yield dir_entry

def get_num_for_url(fn, target_url):
    f = open(fn)
    num_articles = read_int(f, 24, 4)
    url_pointer_list = read_int(f, 32, 8)
    for idx, dir_entry_pos in enumerate(walk_url_pointers(f, url_pointer_list, num_articles)):
        url = read_str(f, dir_entry_pos + 16)
        if url == target_url:
            return idx
    return 0

def set_main_page(fn, target_url):
    bn = get_num_for_url(fn, target_url)
    f = open(fn, 'r+b')
    f.seek(64)
    f.write(struct.pack('<L', bn))

if __name__ == '__main__':
    set_main_page('test.zim', 'Table of Contents')
