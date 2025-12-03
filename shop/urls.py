from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path(网址后缀, 调用的视图函数, 名字)
    # 空字符串 '' 表示网站首页
    path('', views.product_list, name='product_list'),
    # <int:pk> 是一个动态参数，意思是“这里接收一个整数，并把它命名为 pk (Primary Key/主键)”
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # === 新增的用户功能 ===
    # 1. 注册
    path('register/', views.register, name='register'),
    
    # 2. 登录 (指定使用我们将要写的 shop/login.html 模板)
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    
    # 3. 注销 (注销后自动跳转到首页 next_page='/')
    # 注意：Django 5.0之后注销建议使用 POST 请求，但为了实验简单，我们先配好路由
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # ======================

    # 添加到购物车
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # 查看购物车
    path('cart/', views.cart_detail, name='cart_detail'),

    # 删除商品路由
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # 结算路由
    path('checkout/', views.checkout, name='checkout'),

    # 支付页面
    path('payment/<int:order_id>/', views.payment, name='payment'),
    
    # 支付成功处理
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),

    # 订单历史路由
    path('my-orders/', views.order_history, name='order_history'),

    # 销售报表页面
    path('dashboard/', views.sales_dashboard, name='sales_dashboard'),

    # 购物车数量调整 (接收两个参数：商品ID 和 动作)
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),

    # 确认收货路由
    path('confirm-receipt/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),
]