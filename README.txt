.. -*- mode: rst; coding: utf-8 -*-

The latest version of this file can be found at:
http://code.pediapress.com/git/mwlib.zim?p=mwlib.zim;a=blob;f=README.txt

======================================================================
mwlib.zim - zim file writer 
======================================================================

Repacks mwlib zip files into zim files. After installation the writer
option 'zim' will be available in mwlib.

======================================================================
Installation
======================================================================

Download the sources, unpack and run::

  python setup.py install

Required software:

* cython
* lxml
* mwlib (http://code.pediapress.com/git/mwlib)
* pyzim (https://github.com/schmir/pyzim)

pyzim requires zimlib and zimwriter - requirements for that can
be found at http://www.openzim.org/Releases

======================================================================
Test
======================================================================

The installation can be tested on the command line using mw-render.
For example:
mw-render -w zim -c :en -o test.zim Test

======================================================================
Contact/Further Information
======================================================================
For further information please visit our trac instance running at
http://code.pediapress.com
The current development version can also be found there.

======================================================================
License
======================================================================
Copyright (c) 20011 PediaPress GmbH

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution. 

* Neither the name of PediaPress GmbH nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
