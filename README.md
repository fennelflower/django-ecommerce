## 项目简介
本项目是一个基于 Python Django 框架开发的电子商务网站，实现了顾客浏览、购买、下单、邮件通知以及管理员后台管理等功能。

## 代码文件说明
* **manage.py**: Django 项目的管理脚本，用于启动服务器、数据库迁移等。
* **myshop/**: 项目的主配置文件夹。
    * `settings.py`: 项目核心配置（数据库、邮件、时区等）。
    * `urls.py`: 总路由配置。
* **shop/**: 电商功能的主要应用目录。
    * `models.py`: 数据库模型定义（商品 Product, 订单 Order, 订单项 OrderItem）。
    * `views.py`: 业务逻辑处理（首页、详情页、购物车、结算、支付等）。
    * `urls.py`: 应用内部的路由配置。
    * `admin.py`: 后台管理系统的配置。
    * `templates/shop/`: 存放所有 HTML 网页模板。
* **requirements.txt**: 项目依赖库列表。
* **db.sqlite3**: SQLite 数据库文件。

## 如何运行
1. 安装依赖: `pip install -r requirements.txt`
2. 迁移数据库: `python manage.py migrate`
3. 创建管理员: `python manage.py createsuperuser`
4. 启动服务器: `python manage.py runserver`
