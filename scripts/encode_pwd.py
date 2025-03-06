# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : encode_pwd.py
# Time       : 2025/3/5 14:54
# Author     : Feiren Cheng
# Description: 
"""
from passlib.handlers.pbkdf2 import pbkdf2_sha256


pwd = "password123"
print(pbkdf2_sha256.hash(pwd))