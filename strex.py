#! /usr/bin/env python3
"""
String extensions for manipulating strings in Python.

Copyright (c) 2015, Matthew Kelly (Badgerati)
License: MIT (see LICENSE for details)
"""


def is_none(value):
    return value is None

def is_empty(value):
    return str(value) == ''

def is_none_or_empty(value):
    return is_none(value) or is_empty(value)

def safeguard(value, default = ''):
    if is_none_or_empty(value):
        if is_none_or_empty(default):
            return ''
        return default
    return value

