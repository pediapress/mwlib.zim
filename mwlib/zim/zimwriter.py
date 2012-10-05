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
import datetime

from lxml import etree

from mwlib.zim.collection import WebPage, coll_from_zip
from mwlib.zim import config
import pyzim


#pyzim.init_log()

def src2aid(src):
    return sha1(src).hexdigest()

def clean_url(url):
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    if urlparse.urlsplit(url).scheme not in  ['http', 'https', '']:
        return urllib.quote(urllib.unquote(url), safe='/=&+')

    return urlparse.urlunsplit([urllib.quote(urllib.unquote(frag), safe='/=&+')
                                for frag in urlparse.urlsplit(url)])


class ZIPArticleSource(pyzim.IterArticleSource):
    def __init__(self, zipfn, status_callback):
        pyzim.IterArticleSource.__init__(self)
        self.tmpdir = tempfile.mkdtemp()
        self.coll = coll_from_zip(self.tmpdir, zipfn)
        self.aid2article = {}
        self.url2article = {}
        self.status_callback = status_callback
        self.main_page_name = 'Table of Contents'
        self.mainPage = self.main_page_name  # mainPage is a property defined in _pyzim.pyx
        self.metadata = self.set_metadata()

    def __del__(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def dump_toc(self):
        title = self.main_page_name
        article = pyzim.Article(title, aid=title, url=title, mimetype='text/html', namespace='A')

        w = WebPage(coll=self.coll, title=title, url='')
        html = ['<div id="content">', '<h2 style="font-family:sans-serif;">%s</h2>' % self.main_page_name, '<ul style="font-family:sans-serif;">']
        for lvl, webpage in self.coll.outline.walk(cls=WebPage):
            url = clean_url(webpage.canonical_url.encode('utf-8'))
            html.append('<li><a href="%s">%s</a></li>' % (url, webpage.title.encode('utf-8')))

        html.extend(['</ul>', '</div>'])
        html = ''.join(html)
        html += ' '*1000 # kiwix is broken and skips a certain amount of content

        w.tree = w._get_parse_tree(html)
        article.webpage = w
        self.aid2article[title] = article
        return article

    def add_css(self):
        css_path = self.coll.outline.items[0].css_path
        aid = src2aid(css_path)
        self.css_aid = aid
        css = pyzim.Article(aid, aid=aid, url=aid, mimetype='text/css', namespace='-')
        css.filename = css_path
        self.aid2article[aid] = css
        return css

    def set_metadata(self):
        # list below was extracted from http://www.sil.org/iso639-3/iso-639-3_20100707.tab
        iso2_iso3 = {'gv': 'glv', 'gu': 'guj', 'gd': 'gla', 'ga': 'gle', 'gn': 'grn', 'gl': 'glg', 'lg': 'lug', 'lb': 'ltz', 'la': 'lat', 'ln': 'lin', 'lo': 'lao', 'tt': 'tat', 'tr': 'tur', 'ts': 'tso', 'li': 'lim', 'lv': 'lav', 'to': 'ton', 'lt': 'lit', 'lu': 'lub', 'tk': 'tuk', 'th': 'tha', 'ti': 'tir', 'tg': 'tgk', 'te': 'tel', 'ta': 'tam', 'yi': 'yid', 'yo': 'yor', 'de': 'deu', 'da': 'dan', 'dz': 'dzo', 'st': 'sot', 'dv': 'div', 'qu': 'que', 'el': 'ell', 'eo': 'epo', 'en': 'eng', 'zh': 'zho', 'ee': 'ewe', 'za': 'zha', 'mh': 'mah', 'uk': 'ukr', 'eu': 'eus', 'et': 'est', 'es': 'spa', 'ru': 'rus', 'rw': 'kin', 'rm': 'roh', 'rn': 'run', 'ro': 'ron', 'bn': 'ben', 'be': 'bel', 'bg': 'bul', 'ba': 'bak', 'wa': 'wln', 'wo': 'wol', 'bm': 'bam', 'jv': 'jav', 'bo': 'bod', 'bi': 'bis', 'br': 'bre', 'bs': 'bos', 'ja': 'jpn', 'om': 'orm', 'oj': 'oji', 'ty': 'tah', 'oc': 'oci', 'tw': 'twi', 'os': 'oss', 'or': 'ori', 'xh': 'xho', 'ch': 'cha', 'co': 'cos', 'ca': 'cat', 'ce': 'che', 'cy': 'cym', 'cs': 'ces', 'cr': 'cre', 'cv': 'chv', 'cu': 'chu', 've': 'ven', 'ps': 'pus', 'pt': 'por', 'tl': 'tgl', 'pa': 'pan', 'vi': 'vie', 'pi': 'pli', 'is': 'isl', 'pl': 'pol', 'hz': 'her', 'hy': 'hye', 'hr': 'hrv', 'iu': 'iku', 'ht': 'hat', 'hu': 'hun', 'hi': 'hin', 'ho': 'hmo', 'ha': 'hau', 'he': 'heb', 'mg': 'mlg', 'uz': 'uzb', 'ml': 'mal', 'mn': 'mon', 'mi': 'mri', 'ik': 'ipk', 'mk': 'mkd', 'ur': 'urd', 'mt': 'mlt', 'ms': 'msa', 'mr': 'mar', 'ug': 'uig', 'my': 'mya', 'sq': 'sqi', 'aa': 'aar', 'ab': 'abk', 'ae': 'ave', 'ss': 'ssw', 'af': 'afr', 'tn': 'tsn', 'sw': 'swa', 'ak': 'aka', 'am': 'amh', 'it': 'ita', 'an': 'arg', 'ii': 'iii', 'ia': 'ina', 'as': 'asm', 'ar': 'ara', 'su': 'sun', 'io': 'ido', 'av': 'ava', 'ay': 'aym', 'az': 'aze', 'ie': 'ile', 'id': 'ind', 'ig': 'ibo', 'sk': 'slk', 'sr': 'srp', 'nl': 'nld', 'nn': 'nno', 'no': 'nor', 'na': 'nau', 'nb': 'nob', 'nd': 'nde', 'ne': 'nep', 'ng': 'ndo', 'ny': 'nya', 'vo': 'vol', 'zu': 'zul', 'so': 'som', 'nr': 'nbl', 'nv': 'nav', 'sn': 'sna', 'fr': 'fra', 'sm': 'smo', 'fy': 'fry', 'sv': 'swe', 'fa': 'fas', 'ff': 'ful', 'fi': 'fin', 'fj': 'fij', 'sa': 'san', 'fo': 'fao', 'ka': 'kat', 'kg': 'kon', 'kk': 'kaz', 'kj': 'kua', 'ki': 'kik', 'ko': 'kor', 'kn': 'kan', 'km': 'khm', 'kl': 'kal', 'ks': 'kas', 'kr': 'kau', 'si': 'sin', 'sh': 'hbs', 'kw': 'cor', 'kv': 'kom', 'ku': 'kur', 'sl': 'slv', 'sc': 'srd', 'ky': 'kir', 'sg': 'sag', 'se': 'sme', 'sd': 'snd'}

        language = iso2_iso3.get(self.coll.language, 'unknown')
        try:
            source = '://'.join(urlparse.urlsplit(self.coll.outline.items[0].url)[:2])
        except:
            source = 'unknown'

        m = {'Title': self.coll.title,
             'Subtitle': self.coll.subtitle,
             'Creator': config.creator,
             'Date': datetime.date.today().isoformat(),
             'Language': language,
             'Source': source,
             }
        return m

    def add_favicon(self):
        title = 'favicon.png'
        article = pyzim.Article(title, aid=title, url=title, mimetype='image/png', namespace='-')
        article.filename = os.path.join(os.path.dirname(__file__), title)
        self.aid2article[title] = article
        return article

    def __iter__(self):
        num_items = len(self.coll.outline.items)

        yield self.dump_toc()
        yield self.add_css()

        for key, value in self.metadata.items():
            article = pyzim.Article(key, aid=key, url=key, mimetype='text/plain', namespace='M')
            self.aid2article[key] = article
            yield article

        yield self.add_favicon()

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
                if aid in self.aid2article:
                    continue
                mimetype = mimetypes.guess_type(fn)[0]
                img = pyzim.Article(aid, aid=aid, url=aid, mimetype=mimetype, namespace='I')
                img.filename = fn
                self.aid2article[aid] = img
                yield img


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
        elif article.namespace == 'M':
            return self.metadata[aid].encode('utf-8')

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
        for link in webpage.tree.xpath('//link[@type="text/css"]'):
            link.attrib['href'] = '/-/{0}'.format(self.css_aid)

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
    # ZIPArticleSource.create needs a name with .zim extension
    if output.endswith(".zim"):
        rename_to = None
    else:
        rename_to = output
        output = rename_to + ".zim"

    if status_callback:
        status_callback(status='generating zimfile')
    print 'STARTING'
    src = ZIPArticleSource(env, status_callback)
    print 'INITIALIZED'
    src.create(output)
    if rename_to:
        os.rename(output, rename_to)
        output = rename_to
    print 'FINISHED CREATING ZIM FILE'

writer.description = 'ZIM Files'
writer.content_type = 'application/zim' # FIXME: verify/correct
writer.file_extension = 'zim'

writer.options = {
    'lang': {
        'param': 'LANGUAGE',
        'help': 'use translated strings in given language (defaults to "en" for English)',
    },
}

