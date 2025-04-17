#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib


def mymd5(pwd):
    md = hashlib.md5()
    md.update(pwd.encode('utf8'))
    return md.hexdigest()