from django.contrib import admin
from .models import Product, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# 1. 注册商品模型 - 对应实验要求的“商品目录管理”
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'created_at'] # 在列表中显示的字段
    search_fields = ['name'] # 添加搜索框，可以通过名字搜索商品
    list_editable = ['price', 'stock'] # 允许直接在列表页修改价格和库存（非常方便）

# 2. 注册订单模型 - 对应实验要求的“订单管理”
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at'] # 添加右侧过滤器，按状态筛选订单
    inlines = [OrderItemInline] # 在订单详情页直接显示买了哪些东西

# 3. 如果想单独看订单项，也可以注册（可选）
admin.site.register(OrderItem)

# 定义一个新的用户管理类，继承自原来的
class UserAdmin(BaseUserAdmin):
    # 定义一个新函数，专门用来把"用户组"变成字符串显示出来
    def get_groups(self, obj):
        # 获取该用户所有的组，用逗号拼接成字符串
        return ", ".join([g.name for g in obj.groups.all()])
    
    # 给这一列起个名字，叫"所属组"
    get_groups.short_description = '所属组'

    # 关键步骤：重写列表显示的字段
    # 原来的字段 + 我们新写的 get_groups
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')

# 先注销原来的 User 模型 (否则会报错说已经注册过了)
admin.site.unregister(User)

# 用我们需要的新样式重新注册
admin.site.register(User, UserAdmin)