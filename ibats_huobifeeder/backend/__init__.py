#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/6/12 13:47
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from ibats_common.utils.redis import get_redis as get_redis_base
from ibats_huobifeeder.config import config
from ibats_common.backend import engines


def get_redis():
    return get_redis_base(config.REDIS_INFO_DIC['REDIS_HOST'], config.REDIS_INFO_DIC['REDIS_PORT'])


engine_md = engines[config.DB_SCHEMA_MD]
