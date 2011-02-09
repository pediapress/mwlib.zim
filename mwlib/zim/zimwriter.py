#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

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
    def __init__(self, zipfn):
        self.tmpdir = tempfile.mkdtemp()
        self.coll = coll_from_zip(self.tmpdir, zipfn)
        self.aid2article = {}

    def __del__(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def __iter__(self):
        for lvl, webpage in self.coll.outline.walk(cls=WebPage):
            title = webpage.title
            # slashes in the title break correct display in kiwix.
            # don't know if this is a bug in any of the writers or in the reader...
            title = title.replace('/', '')
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
            root = webpage.tree
            self.rewrite_links(root, webpage.url)
            self.rewrite_css_links(root, webpage.url)
            self.rewrite_img_srcs(root, webpage.url)
            self.clean_tree(root)
            return etree.tostring(root)
        elif article.namespace in ['I', '-']:
            fn = self.aid2article[aid].filename
            return open(fn, 'rb').read()

    def rewrite_links(self, root, articleurl):
        for a in root.xpath('//a[@title]'):
            title = a.attrib['title']
            aid = title # FIXME
            if aid in self.aid2article:
                a.attrib['href'] = '/A/{0}'.format(title)
            else:
                a.attrib['href'] = urlparse.urljoin(articleurl, a.attrib['href'])

    def rewrite_css_links(self, root, articleurl):
        for link in root.xpath('//link'):
            href = link.attrib['href']
            aid = src2aid(href)
            if aid in self.aid2article:
                link.attrib['href'] = '/-/{0}'.format(aid)
            else:
                link.attrib['href'] = urlparse.urljoin(articleurl, link.attrib['href'])



    def rewrite_img_srcs(self, root, articleurl):
        for img in root.xpath('//img'):
            src = img.attrib['src']
            aid = src2aid(src)
            if aid in self.aid2article:
                img.attrib['src'] = '/I/{0}'.format(aid)
            else:
                img.attrib['src'] = urlparse.urljoin(articleurl, src)
                #img.attrib['src'] = ''

    def clean_tree(self, root):
        for node in root.xpath('//*[contains(@class, "editsection")]'):
            p = node.getparent()
            if p is not None:
                p.remove(node)


def writer(env, output,
           status_callback=None,
           ):
    print 'STARTING'
    src = ZIPArticleSource(env)
    print 'INITIALIZED'
    src.create(output)
    print 'FINISHED CREATING ZIM FILE'

writer.description = 'ZIM Files'
writer.content_type = 'application/zim' # FIXME: verify/correct
writer.file_extension = 'zim'
