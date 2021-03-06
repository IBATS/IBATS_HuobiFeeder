#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/6/12 13:02
@File    : orm.py
@contact : mmmaaaggg@163.com
@desc    :
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint, TIMESTAMP, text, Date
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.declarative import declarative_base
from ibats_common.utils.db import with_db_session
from ibats_huobi_feeder.backend import engine_md
from ibats_huobi_feeder.config import config
import logging
logger = logging.getLogger()
BaseModel = declarative_base()


class SymbolPair(BaseModel):
    __tablename__ = 'symbol_pair_info'
    id = Column(Integer, autoincrement=True, unique=True)
    market = Column(String(10), primary_key=True)
    base_currency = Column(String(10), primary_key=True)
    quote_currency = Column(String(10), primary_key=True)
    price_precision = Column(Integer)
    amount_precision = Column(Integer)
    symbol_partition = Column(String(12))
    __table_args__ = (
        UniqueConstraint('base_currency', 'quote_currency'),
    )


class MDTick(BaseModel):
    __tablename__ = 'md_min1_tick_bc'
    id = Column(Integer, autoincrement=True, unique=True)
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_date = Column(Date, primary_key=True)
    ts_start = Column(TIMESTAMP)
    ts_curr = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMin1(BaseModel):
    __tablename__ = 'md_min1_bc'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMin1Temp(BaseModel):
    __tablename__ = 'md_min1_bc_temp'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMin60(BaseModel):
    __tablename__ = 'md_min60_bc'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMin60Temp(BaseModel):
    __tablename__ = 'md_min60_bc_temp'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMinDaily(BaseModel):
    __tablename__ = 'md_daily_bc'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


class MDMinDailyTemp(BaseModel):
    __tablename__ = 'md_daily_bc_temp'
    market = Column(String(10), primary_key=True)
    symbol = Column(String(10), primary_key=True)
    ts_start = Column(TIMESTAMP, primary_key=True, server_default=text('CURRENT_TIMESTAMP'))
    ts_curr = Column(TIMESTAMP)
    open = Column(DOUBLE)
    high = Column(DOUBLE)
    low = Column(DOUBLE)
    close = Column(DOUBLE)
    amount = Column(DOUBLE)
    vol = Column(DOUBLE)
    count = Column(DOUBLE)


def init(alter_table=False):
    logger.info(engine_md)
    BaseModel.metadata.create_all(engine_md)
    if alter_table:
        with with_db_session(engine=engine_md) as session:
            show_status_sql_str = f"show table status from {config.DB_SCHEMA_MD} where name=:table_name"
            for table_name, _ in BaseModel.metadata.tables.items():
                row_data = session.execute(show_status_sql_str, params={'table_name': table_name}).first()
                if row_data is None:
                    continue
                if row_data[1].lower() == 'myisam':
                    continue

                logger.info('修改 %s 表引擎为 MyISAM', table_name)
                sql_str = "ALTER TABLE %s ENGINE = MyISAM" % table_name
                session.execute(sql_str)

            sql_str = f"""select table_name from information_schema.columns 
              where table_schema = :table_schema and column_name = 'ts_start' and extra <> ''"""
            table_name_list = [row_data[0]
                               for row_data in session.execute(sql_str, params={'table_schema': config.DB_SCHEMA_MD})]

            for table_name in table_name_list:
                logger.info('修改 %s 表 ts_start 默认值，剔除 on update 默认项', table_name)
                # TimeStamp 类型的数据会被自动设置 default: 'CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP'
                # 需要将 “on update CURRENT_TIMESTAMP”剔除，否则在执行更新时可能会引起错误
                session.execute(f"ALTER TABLE {table_name} CHANGE COLUMN `ts_start` `ts_start` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")

            # This is an issue  https://www.mail-archive.com/sqlalchemy@googlegroups.com/msg19744.html
            session.execute(f"ALTER TABLE {SymbolPair.__tablename__} CHANGE COLUMN `id` `id` INT(11) NULL AUTO_INCREMENT")
            session.commit()
            # This is an issue  https://www.mail-archive.com/sqlalchemy@googlegroups.com/msg19744.html
            session.execute(f"ALTER TABLE {MDTick.__tablename__} CHANGE COLUMN `id` `id` INT(11) NULL AUTO_INCREMENT")
            session.commit()
            # 关于 MDTick 表，由于 partition的原因，改变需要在索引方面做一些调整，这里暂未对其进行程序化处理
            # 需要对原来的旧表进行相应的改变处理，大体的语句如下：
            # """
            #         ALTER TABLE `md_min1_tick_bc`
            # ADD COLUMN `ts_date` DATE NOT NULL AFTER `symbol`,
            # DROP PRIMARY KEY,
            # ADD PRIMARY KEY (`market`, `symbol`, `ts_date`, `ts_curr`),
            # DROP INDEX `id` ,
            # ADD UNIQUE INDEX `id` (`id` ASC, `ts_date` ASC);
            # """
            # 另外，表分区语句如下
            # """
            # ALTER TABLE `bc_md`.`md_min1_tick_bc`
            #  PARTITION BY RANGE(TO_DAYS(ts_date)) (
            #  PARTITION part1 VALUES LESS THAN (TO_DAYS('2018-08-01')),
            #  PARTITION part2 VALUES LESS THAN (TO_DAYS('2018-09-01')),
            #  PARTITION part3 VALUES LESS THAN (TO_DAYS('2018-10-01')),
            #  PARTITION part4 VALUES LESS THAN (TO_DAYS('2018-11-01')),
            #  PARTITION part5 VALUES LESS THAN (TO_DAYS('2018-12-01')),
            #  PARTITION part6 VALUES LESS THAN (TO_DAYS('2019-01-01')),
            #  PARTITION part7 VALUES LESS THAN (TO_DAYS('2019-02-01')),
            #  PARTITION part8 VALUES LESS THAN (TO_DAYS('2019-03-01')),
            #  PARTITION part9 VALUES LESS THAN (TO_DAYS('2019-04-01')),
            #  PARTITION part10 VALUES LESS THAN (TO_DAYS('2019-05-01')),
            #  PARTITION part11 VALUES LESS THAN (TO_DAYS('2019-06-01')),
            #  PARTITION part12 VALUES LESS THAN (TO_DAYS('2019-07-01')),
            #  PARTITION part13 VALUES LESS THAN (TO_DAYS('2019-08-01')),
            #  PARTITION part14 VALUES LESS THAN (TO_DAYS('2019-09-01')),
            #  PARTITION part15 VALUES LESS THAN (TO_DAYS('2019-10-01')),
            #  PARTITION part16 VALUES LESS THAN (TO_DAYS('2019-11-01')),
            #  PARTITION part17 VALUES LESS THAN (TO_DAYS('2019-12-01')),
            #  PARTITION part18 VALUES LESS THAN (MAXVALUE)
            #  ) ;
            # """

    logger.info("所有表结构建立完成")


if __name__ == "__main__":
    init()
