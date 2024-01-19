#coding=utf-8

from views import *
import os

settings={
    'handlers':[
        (r'^/login/$',LoginHandler),
        (r'^/center/$',CenterHandler)
    ],'template_path':os.path.join(os.getcwd(),'templates')
}