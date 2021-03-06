# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import hashlib

import strutil

from flask import g,request,redirect

from flask import current_app as app

def set_logined(req,resp,ukey,timeout=None):
    kargs = {
            'path':'/','secure':None
            }
    date_create = int(time.time())
    if timeout is not None:
        assert isinstance(timeout,(int,long)),'timeout must be an integer or None'
        kargs['max_age'] = timeout
        kargs['expires'] = strutil.cookie_date(date_create + timeout)
    else:
        timeout = 0
    date_create = str(date_create)
    sha1sum = hashlib.sha1(app.config.get('SECRET_KEY','') + ukey + date_create).hexdigest()
    resp.set_cookie('is_logined','True',**kargs)
    resp.set_cookie('ukey',ukey,**kargs)
    resp.set_cookie('date_create',date_create,**kargs)
    resp.set_cookie('token',sha1sum,**kargs)
    

def set_logout(req,resp):
    req.session.flush()
    resp.delete_cookie('is_logined')
    resp.delete_cookie('ukey')
    resp.delete_cookie('date_create')
    resp.delete_cookie('token')


def is_logined(req):
    is_logined = req.cookies.get('is_logined')
    if not is_logined:
        return False
    ukey = req.cookies.get('ukey','')
    date_create = req.cookies.get('date_create','')
    token = req.cookies.get('token','')
    if hashlib.sha1(app.config.get('SECRET_KEY') + ukey + date_create).hexdigest() == token:
        return True
    return False


def user_required(f):
    '''必须登陆后才能访问的视图'''
    def decorator(*args,**kwargs):
        if not is_logined(request):
            return redirect('/login?next=%s' % request.path)
        return f(*args,**kwargs)
    decorator.__name__ = f.__name__
    return decorator


