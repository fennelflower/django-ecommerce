from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

# 商品模型：对应实验要求的“商品目录”
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="商品名称")
    description = models.TextField(verbose_name="商品描述")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    stock = models.PositiveIntegerField(default=0, verbose_name="库存")
    # image 字段需要刚才安装的 Pillow 库
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="商品图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上架时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品管理"

# 订单模型：对应实验要求的“订单管理”
class Order(models.Model):
    # 订单状态选项
    STATUS_CHOICES = (
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '发货中'),   
        ('confirmed', '已收货'), 
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单用户")
    shipping_address = models.CharField(max_length=255, verbose_name="收货地址", blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="总价")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="订单状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")

    def __str__(self):
        return f"订单号 {self.id} - {self.user.username}"

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单管理"

# 订单项：记录每个订单里买了什么商品和数量
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")

    def __str__(self):
        return f"{self.id}"
    

# 监听器：当 OrderItem 发生变化（保存或删除）时，自动执行 update_order_total
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    order = instance.order
    # 重新计算该订单下所有条目的总价
    # aggregate(Sum...) 会返回 {'subtotal__sum': 123.00}
    # 注意：我们需要先在 OrderItem 里计算好单行的小计，或者直接在这里用 Quantity * Price 计算
    
    # 简单粗暴的方法：遍历重算
    total = 0
    for item in order.items.all():
        total += item.price * item.quantity
    
    order.total_price = total
    order.save()


 # === 用户行为日志模型 ===

class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    # 行为类型：浏览(View) / 购买(Buy)
    action_type = models.CharField(max_length=10, choices=(('view', '浏览'), ('buy', '购买')), verbose_name="行为类型")
    # 行为描述：比如 "查看了 iPhone 15"
    description = models.CharField(max_length=255, verbose_name="行为描述")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp}"

    class Meta:
        verbose_name = "用户日志"
        verbose_name_plural = "客户浏览/购买日志"
        ordering = ['-timestamp'] # 最新发生的排在前面