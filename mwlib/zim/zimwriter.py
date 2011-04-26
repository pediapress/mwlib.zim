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
import urllib


from lxml import etree

from mwlib.zim.collection import WebPage, coll_from_zip
from mwlib.zim.setmainpage import set_main_page

import pyzim


#pyzim.init_log()

def src2aid(src):
    return sha1(src).hexdigest()

def clean_url(url):
    return urlparse.urlunsplit([urllib.quote(urllib.unquote(frag), safe='/=&+')
                                for frag in urlparse.urlsplit(url)])


class ZIPArticleSource(pyzim.IterArticleSource):
    def __init__(self, zipfn, status_callback):
        self.tmpdir = tempfile.mkdtemp()
        self.coll = coll_from_zip(self.tmpdir, zipfn)
        self.aid2article = {}
        self.url2article = {}
        self.status_callback = status_callback
        self.main_page_name = 'Table of Contents'


    def __del__(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def dump_toc(self, coll):
        title = self.main_page_name
        article = pyzim.Article(title, aid=title, url=title, mimetype='text/html', namespace='A')

        w = WebPage(coll=coll, title=title, url='')
        html = ['<div id="content">', '<h2 style="font-family:sans-serif;">%s</h2>' % self.main_page_name, '<ul style="font-family:sans-serif;">']

        for lvl, webpage in coll.outline.walk(cls=WebPage):
            url = clean_url(webpage.canonical_url.encode('utf-8'))
            html.append('<li><a href="%s">%s</a></li>' % (url, webpage.title.encode('utf-8')))

        html.extend(['</ul>', '</div>'])
        html = ''.join(html)
        html += ' '*1000 # kiwix is broken and skips a certain amount of content
        w.tree = w._get_parse_tree(html)
        article.webpage = w
        return (article, title)

    def __iter__(self):
        num_items = len(self.coll.outline.items)
        article, aid =  self.dump_toc(self.coll)
        self.aid2article[aid] = article
        yield article
        for n, (lvl, webpage) in enumerate(self.coll.outline.walk(cls=WebPage)):
            if self.status_callback:
                self.status_callback(progress=100*n/num_items)
            title = webpage.title
            title = title.encode('utf-8')
            title = title.replace('/', '') # workaround for bug in kiwix < 0.9 alpha8
            aid = title # webpage.id FIXME
            url = aid # FIXME
            article = pyzim.Article(title, aid=aid, url=url, mimetype='text/html', namespace='A')
            article.webpage = webpage
            webpage.aid = aid
            self.aid2article[aid] = article
            self.url2article[clean_url(webpage.canonical_url.encode('utf-8'))] = article
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
            href = a.get('href')
            if href.startswith('#'):
                target = '/A/{0}{1}'.format(clean_url(webpage.aid), clean_url(href))
            else:
                url = clean_url(urlparse.urljoin(webpage.url.encode('utf-8'), href))
                if url in self.url2article:
                    target = '/A/{0}'.format(clean_url(self.url2article[url].aid))
                else:
                    target = url
            a.attrib['href'] = target

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
           lang=None,
           ):
    if status_callback:
        status_callback(status='generating zimfile')
    print 'STARTING'
    src = ZIPArticleSource(env, status_callback)
    print 'INITIALIZED'
    src.create(output)
    print 'FINISHED CREATING ZIM FILE'
    set_main_page(output, src.main_page_name)
    print 'SET MAIN PAGE'

writer.description = 'ZIM Files'
writer.content_type = 'application/zim' # FIXME: verify/correct
writer.file_extension = 'zim'

writer.options = {
    'lang': {
        'param': 'LANGUAGE',
        'help': 'use translated strings in given language (defaults to "en" for English)',
    },
}

