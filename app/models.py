from django.db import models

# Create your models here.

class BaseModel(models.Model):
    img = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    trackid = models.CharField(max_length=10)

    class Meta:
        abstract = True

class Wheel(BaseModel):
    class Meta:
        db_table = 'axf_wheel'

class Nav(BaseModel):
    class Meta:
        db_table = 'axf_nav'

class Mustbuy(BaseModel):
    class Meta:
        db_table = 'axf_mustbuy'

class Shop(BaseModel):
    class Meta:
        db_table = 'axf_shop'

#商品列表
class Mainshow(models.Model):
    trackid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100)
    categoryid = models.CharField(max_length=10)
    brandname = models.CharField(max_length=100)

    img1 = models.CharField(max_length=100)
    childcid1 = models.CharField(max_length=10)
    productid1 = models.CharField(max_length=10)
    longname1 = models.CharField(max_length=100)
    price1 = models.CharField(max_length=10)
    marketprice1 = models.CharField(max_length=10)

    img2 = models.CharField(max_length=100)
    childcid2 = models.CharField(max_length=10)
    productid2 = models.CharField(max_length=10)
    longname2 = models.CharField(max_length=100)
    price2 = models.CharField(max_length=10)
    marketprice2 = models.CharField(max_length=10)

    img3 = models.CharField(max_length=100)
    childcid3 = models.CharField(max_length=10)
    productid3 = models.CharField(max_length=10)
    longname3 = models.CharField(max_length=100)
    price3 = models.CharField(max_length=10)
    marketprice3 = models.CharField(max_length=10)

    class Meta:
        db_table = 'axf_mainshow'


#分类
class Foodtypes(models.Model):
    typeid = models.CharField(max_length=10)
    typename = models.CharField(max_length=100)
    childtypenames = models.CharField(max_length=200)
    typesort = models.IntegerField()

    class Meta:
        db_table = 'axf_foodtypes'


# 商品模型类
class Goods(models.Model):
    # 商品ID
    productid = models.CharField(max_length=10)
    # 商品图片
    productimg = models.CharField(max_length=200)
    # 商品名称
    productname = models.CharField(max_length=100)
    # 商品长名字
    productlongname = models.CharField(max_length=200)
    # 是否是精选
    isxf = models.IntegerField()
    # 是否买一送一
    pmdesc = models.IntegerField()
    # 规格
    specifics = models.CharField(max_length=100)
    # 价格
    price = models.FloatField()
    # 超市价格
    marketprice = models.FloatField()
    # 分类ID
    categoryid = models.CharField(max_length=10)
    # 子类ID
    childcid = models.CharField(max_length=10)
    # 子类名字
    childcidname = models.CharField(max_length=50)
    # 详情id
    dealerid = models.CharField(max_length=10)
    # 库存量
    storenums = models.IntegerField()
    # 销售量
    productnum = models.IntegerField()

    class Meta:
        db_table = 'axf_goods'

class User(models.Model):
    email = models.CharField(max_length=40,unique=True)
    password = models.CharField(max_length=256)
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100,default='axf.png')
    rank = models.IntegerField(default=1)

    class Meta:
        db_table = 'axf_user'

class Cart(models.Model):
    user = models.ForeignKey(User)
    goods = models.ForeignKey(Goods)
    number = models.IntegerField()
    isselect = models.BooleanField(default=True) #是否全选
    isdelete = models.BooleanField(default=False)

    class Meta:
        db_table = 'axf_cart'

#一个用户对应多个订单
class Order(models.Model):
    user = models.ForeignKey(User)
    createtime = models.DateTimeField(auto_now_add=True)  #订单生成时间
    updatetime = models.DateTimeField(auto_now=True)  #更新时间
    #-1过期    0未付款 1 已付款  待发货  2待收货 3评价 4已评价
    status= models.IntegerField(default=0)
    identifier = models.CharField(max_length=256)


    #一个订单对应多个商品
class OrderGoods(models.Model):
    order = models.ForeignKey(Order)
    goods = models.ForeignKey(Goods)
    number = models.IntegerField()