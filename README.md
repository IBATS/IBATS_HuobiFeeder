# [Huobi Feeder](https://github.com/IBATS/IBATS_HuobiFeeder)
连接火币交易所

通过 feed.md_feeder 接受事实行情及补充历史数据

通过 backend.handler 处理实时行情，保持到数据库，进行redis广播

该项目作为 IBATS 框架的 Feeder 组件可独立部署



## 安装

#### 系统环境要求：

> Python 3.6 
>
> MySQL 5.7  [配置方法总结了一下，见下文](#mysql-配置方法)
>
> Redis 3.0.6 

#### 安装必要python包

Windows环境

> pip install -r requirements.txt

Linux环境

> pip3 install -r requirements.txt

#### 配置文件

config.py
基础配置

1 ) MYSQL数据库用户名、密码
```python
DB_SCHEMA_MD = 'md_huobi'
DB_URL_DIC = {
    DB_SCHEMA_MD: 'mysql://m*:****@10.0.3.66/' + DB_SCHEMA_MD
}
```
2 ) 火币交易所 EXCHANGE_ACCESS_KEY、EXCHANGE_SECRET_KEY
```python
# api configuration
EXCHANGE_ACCESS_KEY = ""
EXCHANGE_SECRET_KEY = ""
```

可选配置

1 ) Redis 路径
```python
# redis info
REDIS_PUBLISHER_ENABLE = True
REDIS_INFO_DIC = {'REDIS_HOST': 'localhost',
                  'REDIS_PORT': '6379',
                  }
```
#### 启动方法

直接运行 run.bat

启动过程中会自动建立相应数据库表结构



## 存储及服务

存储mysql数据库

> md_min1_tick_bc  tick数据
>
> my_min1_bc   一分钟数据
>
> md_min60_bc  一小时数据
>
> md_daily_bc  日数据

## 实时行情Redis广播服务

channel格式：

```
md.{market}.{period}.{symbol}
#    例如：
#    md.huobi.Min1.ethusdt
#    md.huobi.Tick.eosusdt
```
订阅方式：
SUBSCRIBE md.huobi.Tick.eosusdt


## 欢迎赞助

#### 微信

![微信支付](https://github.com/mmmaaaggg/ABAT_trader_4_blockchain/blob/master/mass/webchat_code200.png?raw=true)

#### 支付宝

![微信支付](https://github.com/mmmaaaggg/ABAT_trader_4_blockchain/blob/master/mass/alipay_code200.png?raw=true)

#### 微信打赏（￥10）

![微信打赏](https://github.com/mmmaaaggg/ABAT_trader_4_blockchain/blob/master/mass/dashang_code200.png?raw=true)

## MySQL 配置方法

 1. Ubuntu 18.04 环境下安装 MySQL，5.7
 
    ```bash
    sudo apt install mysql-server
    ```
 2. 默认情况下，没有输入用户名密码的地方，因此，安装完后需要手动重置Root密码，方法如下：

    ```bash
    cd /etc/mysql/debian.cnf
    sudo more debian.cnf
    ```
    出现类似这样的东西
    ```bash
    # Automatically generated for Debian scripts. DO NOT TOUCH!
    [client]
    host     = localhost
    user     = debian-sys-maint
    password = j1bsABuuDRGKCV5s
    socket   = /var/run/mysqld/mysqld.sock
    [mysql_upgrade]
    host     = localhost
    user     = debian-sys-maint
    password = j1bsABuuDRGKCV5s
    socket   = /var/run/mysqld/mysqld.sock
    ```

    以debian-sys-maint为用户名登录，密码就是debian.cnf里那个 password = 后面的东西。
    使用mysql -u debian-sys-maint -p 进行登录。
    进入mysql之后修改MySQL的密码，具体的操作如下用命令：
    ```mysql
    use mysql;
    
    update user set authentication_string=PASSWORD("Dcba4321") where user='root';
    
    update user set plugin="mysql_native_password"; 
     
    flush privileges;
    ```
 3. 然后就可以用过root用户登陆了

    ```bash
    mysql -uroot -p
    ```

 4. 创建用户 mg 默认密码 Abcd1234

    ```mysql
    CREATE USER 'mg'@'%' IDENTIFIED BY 'Abcd1234';
    ```
 5. 创建数据库 bc_md

    ```mysql
    CREATE DATABASE `bc_md` default charset utf8 collate utf8_general_ci;
    ```
 6. 授权

    ```mysql
    grant all privileges on bc_md.* to 'mg'@'localhost' identified by 'Abcd1234'; 
    
    flush privileges; #刷新系统权限表
    ```
 
 ## 2019-03-19 版本升级
 对 md_min1_tick_bc 表进行分区处理以应对其不断增长的数据库，为此需要对索引进行相应的调整，旧表需要进行相应的更新以适应新的程序。表修改语句如下：
1） 增加ts_date列，同时改变表主键及索引结构
 ```mysql
ALTER TABLE `md_min1_tick_bc` 
ADD COLUMN `ts_date` DATE NOT NULL AFTER `symbol`,
DROP PRIMARY KEY,
ADD PRIMARY KEY (`market`, `symbol`, `ts_date`, `ts_curr`),
DROP INDEX `id` ,
ADD UNIQUE INDEX `id` (`id` ASC, `ts_date` ASC);
```

2） 进行表分区处理
```mysql
ALTER TABLE `bc_md`.`md_min1_tick_bc` 
 PARTITION BY RANGE(TO_DAYS(ts_date)) ( 
 PARTITION part1 VALUES LESS THAN (TO_DAYS('2018-08-01')), 
 PARTITION part2 VALUES LESS THAN (TO_DAYS('2018-09-01')), 
 PARTITION part3 VALUES LESS THAN (TO_DAYS('2018-10-01')), 
 PARTITION part4 VALUES LESS THAN (TO_DAYS('2018-11-01')), 
 PARTITION part5 VALUES LESS THAN (TO_DAYS('2018-12-01')), 
 PARTITION part6 VALUES LESS THAN (TO_DAYS('2019-01-01')), 
 PARTITION part7 VALUES LESS THAN (TO_DAYS('2019-02-01')), 
 PARTITION part8 VALUES LESS THAN (TO_DAYS('2019-03-01')), 
 PARTITION part9 VALUES LESS THAN (TO_DAYS('2019-04-01')), 
 PARTITION part10 VALUES LESS THAN (TO_DAYS('2019-05-01')), 
 PARTITION part11 VALUES LESS THAN (TO_DAYS('2019-06-01')), 
 PARTITION part12 VALUES LESS THAN (TO_DAYS('2019-07-01')), 
 PARTITION part13 VALUES LESS THAN (TO_DAYS('2019-08-01')), 
 PARTITION part14 VALUES LESS THAN (TO_DAYS('2019-09-01')), 
 PARTITION part15 VALUES LESS THAN (TO_DAYS('2019-10-01')), 
 PARTITION part16 VALUES LESS THAN (TO_DAYS('2019-11-01')), 
 PARTITION part17 VALUES LESS THAN (TO_DAYS('2019-12-01')), 
 PARTITION part18 VALUES LESS THAN (MAXVALUE)
 ) ; 
```