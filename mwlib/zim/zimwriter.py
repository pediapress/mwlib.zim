#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

from __future__ import division

from hashlib import sha1
import mimetypes
import os
import shutil
import tempfile
import urlparse

from lxml import etree

from mwlib.zim.collection import WebPage, coll_from_zip
import pyzim


#pyzim.init_log()

def src2aid(src):
    return sha1(src).hexdigest()


class ZIPArticleSource(pyzim.IterArticleSource):
    def __init__(self, zipfn, status_callback):
        self.tmpdir = tempfile.mkdtemp()
        self.coll = coll_from_zip(self.tmpdir, zipfn)
        self.aid2article = {}
        self.status_callback = status_callback

    def __del__(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def __iter__(self):
        num_items = len(self.coll.outline.items)
        for n, (lvl, webpage) in enumerate(self.coll.outline.walk(cls=WebPage)):
            if self.status_callback:
                self.status_callback(progress=n/num_items)
	    title = webpage.title
	    title = title.encode('utf-8')
            title = title.replace('/', '') # workaround for bug in kiwix < 0.9 alpha8
            aid = title # webpage.id FIXME
            url = aid # FIXME
            article = pyzim.Article(title, aid=aid, url=url, mimetype='text/html', namespace='A')
            article.webpage = webpage
            self.aid2article[aid] = article
	    yield article
            for src, fn in webpage.images.items():
                aid = src2aid(src)
                title = aid # TODO
                url = aid
                mimetype = mimetypes.guess_type(fn)[0]
                img = pyzim.Article(title, aid=aid, url=url, mimetype=mimetype, namespace='I')
                img.filename = fn
                self.aid2article[aid] = img
                yield img

            if webpage.css_path:
                aid = src2aid(webpage.css_path)
                title = aid # TODO
                url = aid
                mimetype = 'text/css'
                css = pyzim.Article(title, aid=aid, url=url, mimetype=mimetype, namespace='-')
                css.filename = webpage.css_path
                self.aid2article[aid] = css
                yield css

    def get_data(self, aid):
        article = self.aid2article[aid]
        if article.namespace == 'A':
            webpage = self.aid2article[aid].webpage
            self.rewrite_links(webpage)
            self.rewrite_css_links(webpage)
            self.rewrite_img_srcs(webpage)
            self.removeNodesCustom(webpage)
	    self.setTitle(webpage)
	    html = etree.tostring(webpage.tree)
            return html
        elif article.namespace in ['I', '-']:
            fn = self.aid2article[aid].filename
            return open(fn, 'rb').read()

    def rewrite_links(self, webpage):
        for a in webpage.tree.xpath('//a'):
            title = a.attrib.get('title') or None
            aid = title # FIXME
            if aid in self.aid2article:
                a.attrib['href'] = '/A/{0}'.format(title)
            else:
                a.attrib['href'] = urlparse.urljoin(webpage.url, a.attrib['href'])

    def rewrite_css_links(self, webpage):
        for link in webpage.tree.xpath('//link'):
            href = link.attrib['href']
            aid = src2aid(href)
            if aid in self.aid2article:
                link.attrib['href'] = '/-/{0}'.format(aid)
            else:
                link.attrib['href'] = urlparse.urljoin(webpage.url, link.attrib['href'])



    def rewrite_img_srcs(self, webpage):
        for img in webpage.tree.xpath('//img'):
            src = img.attrib['src']
            aid = src2aid(src)
            if aid in self.aid2article:
                img.attrib['src'] = '/I/{0}'.format(aid)
            else:
                img.attrib['src'] = urlparse.urljoin(webpage.url, src)
                #img.attrib['src'] = ''

    def removeNodesCustom(self, webpage):
        queries = webpage.config('remove', [])
        for klass in webpage.config('remove_class', []):
            queries.append('.//*[contains(@class, "{0}")]'.format(klass))
        for id in webpage.config('remove_id', []):
            queries.append('.//*[contains(@id, "{0}")]'.format(id))
        for query in queries:
            for node in webpage.tree.xpath(query):
                p = node.getparent()
                if len(p):
                    p.remove(node)


    def setTitle(self, webpage):
	title_node = webpage.tree.find('.//title')
	if not title_node:
	    title_node = etree.Element('title')
	title_node.text = webpage.title
	head_node = webpage.tree.find('.//head')
	head_node.append(title_node)

def writer(env, output,
           status_callback=None,
           ):
    if status_callback:
        status_callback(status='generating zimfile')
    print 'STARTING'
    src = ZIPArticleSource(env, status_callback)
    print 'INITIALIZED'
    src.create(output)
    print 'FINISHED CREATING ZIM FILE'

writer.description = 'ZIM Files'
writer.content_type = 'application/zim' # FIXME: verify/correct
writer.file_extension = 'zim'
