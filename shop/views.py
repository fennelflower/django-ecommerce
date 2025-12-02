from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm # Django自带的注册表单工具
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from .forms import EmailValidationForm
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Order, OrderItem, UserLog

def product_list(request):
    # 1. 从数据库读取所有商品
    products = Product.objects.all()
    # 2. 把商品打包成一个字典
    context = {'products': products}
    # 3. 渲染页面：把数据传给 'product_list.html' 这个模板文件
    return render(request, 'shop/product_list.html', context)


def product_detail(request, pk):
    # 1. 尝试获取 ID 为 pk 的商品
    # 如果找到了，就赋值给 product；如果找不到（比如 ID=999），直接返回 404 错误页面
    product = get_object_or_404(Product, pk=pk)
    
    # === 新增：记录浏览日志 ===
    # 只有登录用户才记录，防止游客刷屏（也可以去掉 if 记录所有人）
    if request.user.is_authenticated:
        UserLog.objects.create(
            user=request.user,
            action_type='view',
            description=f"查看商品：{product.name}"
        )
    
    # 2. 打包数据
    context = {'product': product}
    
    # 3. 渲染详情页模板
    return render(request, 'shop/product_detail.html', context)


def register(request):
    if request.method == 'POST':
        # 如果用户提交了表单 (点了注册按钮)
        form = EmailValidationForm(request.POST)
        if form.is_valid():
            # 1. 保存新用户到数据库
            user = form.save()
            # 2. 注册完直接让他自动登录 (提升体验)
            login(request, user)
            # 3.以此跳转回首页
            return redirect('product_list')
    else:
        # 如果用户只是刚打开网页 (GET请求)
        form = EmailValidationForm()
    
    return render(request, 'shop/register.html', {'form': form})


# 1. 添加商品到购物车
@require_POST  # 只允许通过 POST 请求访问（安全）
def add_to_cart(request, product_id):
    # 初始化购物车：如果 session 里没有 'cart'，就新建一个空字典
    cart = request.session.get('cart', {})
    
    # 将 product_id 转为字符串（session 的 key 必须是字符串）
    product_id = str(product_id)
    
    # 如果车里已经有这件商品，数量 +1；如果没有，设为 1
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    
    # 保存购物车回 session
    request.session['cart'] = cart
    
    # 添加成功后，跳转到“购物车详情页”
    return redirect('cart_detail')

# 2. 查看购物车页面
@login_required # 只有登录用户才能看购物车 (可选，为了实验简单建议加上)
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = [] # 用来存放具体的商品对象和数量
    total_price = 0 # 总价
    
    # 遍历购物车字典 {'1': 2, ...}
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity # 小计：单价 x 数量
        total_price += subtotal
        
        # 把所有信息打包
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart_detail.html', context)

# 3. 从购物车删除商品
@require_POST  # 为了安全，修改数据的操作建议用 POST 请求
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    
    # 将 ID 转为字符串（因为存进去时是字符串）
    product_id = str(product_id)
    
    # 如果车里确实有这个商品，就删掉它
    if product_id in cart:
        del cart[product_id]
        # 这一步很关键：修改完字典后，必须重新赋值给 session 才能保存
        request.session['cart'] = cart
    
    # 删完刷新购物车页面
    return redirect('cart_detail')


# 1. 下单 (点击"去结算"后执行，只生成订单，不发邮件)
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
    
    if request.method == 'POST':
        # 创建订单
        order = Order.objects.create(user=request.user, status='pending')
        
        total_price = 0
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            price = product.price
            subtotal = price * quantity
            total_price += subtotal
            
            OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=quantity
            )
        
        # 更新总价
        order.total_price = total_price
        order.save()
        
        # 清空购物车
        del request.session['cart']
        
        # 【关键变化】下单后，不再直接成功，而是跳转到"支付页面"
        return redirect('payment', order_id=order.id)
        
    return redirect('cart_detail')

# 2. 支付页面 (展示二维码，让用户确认)
@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/payment.html', {'order': order})

# 3. 处理支付 (用户点击"确认支付"后执行)
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # 修改状态为"已支付"
        order.status = 'paid'
        order.save()
        
        # === 新增：记录购买日志 ===
        UserLog.objects.create(
            user=request.user,
            action_type='buy',
            description=f"成功支付订单 #{order.id}，金额 ￥{order.total_price}"
        )
        # ==========================

        # === 邮件发送逻辑移动到这里 ===
        order_items_text = "\n".join([f"{item.product.name} x {item.quantity}" for item in order.items.all()])
        
        subject = f"支付成功 - 订单号 #{order.id}"
        message = f"""
        亲爱的 {request.user.username}:
        
        您的付款已收到！
        
        订单详情:
        --------------------------
        {order_items_text}
        --------------------------
        总计: ￥{order.total_price}
        """
        # 发送邮件
        send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email or 'user@example.com'])
        
        return render(request, 'shop/order_success.html', {'order': order})
    
    return redirect('product_list')


@login_required
def order_history(request):
    # 查询当前用户的所有订单，按时间倒序排列(最新的在前面)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})


@staff_member_required # 只有管理员(员工)才能看，普通用户看不了
def sales_dashboard(request):
    # 1. 计算总销售额 (只算已支付的)
    # aggregate 会返回一个字典: {'total_price__sum': 12345.00}
    revenue_data = Order.objects.filter(status='paid').aggregate(Sum('total_price'))
    total_revenue = revenue_data['total_price__sum'] or 0
    
    # 2. 计算总订单数 (只算已支付的)
    total_orders = Order.objects.filter(status='paid').count()
    
    # 3. 热销商品排行 (稍微复杂一点的高级查询)
    # 逻辑：从 OrderItem 表查，按商品分组，把数量加起来，然后倒序排列，取前 5 名
    hot_products = OrderItem.objects.filter(order__status='paid') \
        .values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:5]
        
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'hot_products': hot_products,
    }
    
    return render(request, 'shop/sales_dashboard.html', context)