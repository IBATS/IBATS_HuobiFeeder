#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/12/5 18:27
@File    : immigration.py
@contact : mmmaaaggg@163.com
@desc    : 仅用于从旧schema迁移到新的数据库使用
"""
from ibats_common.utils.db import execute_sql
from ibats_huobi_feeder.backend import engine_md
import logging

logger = logging.getLogger()


def immigrate_data(table_name, from_schema):
    sql_str = f"insert into `{table_name}` select * from `{from_schema}`.`{table_name}`"
    insert_count = execute_sql(engine_md, sql_str)
    logger.debug('迁移 %s 完成，迁移数据 %d 条', table_name, insert_count)


def create_table_and_immigrate_data(table_name, from_schema):
    sql_str = f"create table `{table_name}` like `{from_schema}`.`{table_name}`"
    execute_sql(engine_md, sql_str)
    logger.debug('创建 %s 完成', table_name)
    immigrate_data(table_name, from_schema)


if __name__ == "__main__":
    table_name, from_schema = 'md_min1_tick_bc', 'bc_md'
    immigrate_data(table_name, from_schema)

    table_name, from_schema = 'md_min1_bc', 'bc_md'
    immigrate_data(table_name, from_schema)
