import hashlib
import random
import time
from urllib.parse import parse_qs

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from app.models import Wheel,Nav,Mustbuy,Shop,Mainshow,Foodtypes,Goods,User,Cart,OrderGoods,Order

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django_redis import cache
from django.core.cache import cache

from app.alipay import alipay


def home(request):
    #轮播图
    wheels = Wheel.objects.all()
    navs = Nav.objects.all()
    mustbuys = Mustbuy.objects.all()
    shoplist = Shop.objects.all()
    shophead = shoplist[0]
    shoptabs = shoplist[1:3]
    shopclass= shoplist[3:7]
    shopcommends = shoplist[7:11]
    mainshows = Mainshow.objects.all()

    response_dir = {
        'wheels':wheels,
        'navs':navs,
        'mustbuys':mustbuys,
        'shophead':shophead,
        'shoptabs':shoptabs,
        'shopclass':shopclass,
        'shopcommends':shopcommends,
        'mainshows':mainshows,

    }
    return render(request,'home/home.html',context=response_dir)

def market(request, childid='0' ,sortid='0'):
    foodtypes = Foodtypes.objects.all()


    # 根据 分类ID 获取对应分类信息
    # goods_list = Goods.objects.all()[0:5]   #展示所有商品
    #默认打开热销榜（显示的商品应该过滤出是typeid是热销榜）
    # goods_list = Goods.objects.filter(categoryid=categoryid)

    #客户端需要记录点击分类的下标index[cookies  自动携带」
    #jquery.cookie.js 需要导包（里面有set.get cookie）在js文件中设置
    index = int(request.COOKIES.get('index','0')) #开始没有点击没有cookies 需要设置给默认值

    #根据index获取对应的分类ID
    categoryid = foodtypes[index].typeid   #下标要转为数字类型

    #根据分类id获取对应分类信息
    goods_list = Goods.objects.filter(categoryid=categoryid)

    #获取子类信息
    childtypenames= foodtypes[index].childtypenames

    #将对应子类拆分出来
    childtype_list=[]   #存储子类列表信息
    for item in childtypenames.split('#'):
        # item >> 全部分类：0
        # item >> 子类名称: 子类id
        item_arr = item.split(':')
        temp_dir = {
            'name':item_arr[0],
            'id':item_arr[1]
        }
        childtype_list.append(temp_dir)


    if childid == '0':
        goods_list = Goods.objects.filter(categoryid=categoryid)
    else:
        goods_list = Goods.objects.filter(categoryid=categoryid).filter(childcid=childid)

    #排序
    if sortid == '1':
        goods_list = goods_list.order_by('-productnum')
    elif sortid == '2':
        goods_list = goods_list.order_by('price')
    elif sortid == '3':
        goods_list = goods_list.order_by('-price')

    response_dir = {
        'foodtypes': foodtypes,
        'goods_list': goods_list,
        'childtype_list': childtype_list,
        'childid': childid,


    }


    #获取购物车信息（需先登录）
    token = request.session.get('token')
    userid = cache.get(token)  #根据token拿到用户
    if userid:
        user = User.objects.get(pk=userid)#有用户就有购物车
        carts = user.cart_set.all()#类似于object
        response_dir['carts'] = carts





    return render(request,'market/market.html',context=response_dir)

def cart(request):
    # carts =Cart.objects.all()   #获取所有购物车信息
    # carts = Cart.objects.filter(number__gt=0)
    # return render(request,'cart/cart.html',context={'carts':carts})
    token = request.session.get('token')
    userid = cache.get(token)
    if userid:  # 有登录才显示
        user = User.objects.get(pk=userid)
        carts = user.cart_set.filter(number__gt=0)

        isall = True
        for cart in carts:
            if not cart.isselect:
                isall = False

        return render(request, 'cart/cart.html', context={'carts': carts, 'isall': isall})
    else:  # 未登录不显示
        return render(request, 'cart/no-login.html')

def mine(request):
    token = request.session.get('token')
    userid = cache.get(token)
    response_data = {
        'user': None
    }
    if userid:
        user = User.objects.get(pk=userid)
        response_data['user'] = user

        orders = user.order_set.all()
        # 待付款
        response_data['waitpay'] = orders.filter(status=0).count()
        # 待发货
        response_data['paydone'] = orders.filter(status=1).count()

    return render(request, 'mine/mine.html', context=response_data)

def login(request):
    if request.method == 'GET':
        return render(request, 'mine/login.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        back = request.COOKIES.get('back')   #重定向位置
        print(back)
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            if user.password == generate_password(password):

                token = generate_token()   #更新token
                cache.set(token,user.id,60*60*24*3)  #状态保持
                #传递客户端
                request.session['token']=token
                # return redirect('axf:mine')

                if back == 'mine':
                    return redirect('axf:mine')
                else:
                    return redirect('axf:marketbase')

            else:
                return render(request, 'mine/login.html', context={'ps_err': '密码错误'})
        else:
            return render(request,'mine/login.html',context={'user_err':'用户不存在' })
    # return render(request,'mine/mine.html')

def logout(request):
    request.session.flush()

    return render(request,'mine/mine.html')


def generate_password(param):
    md5 = hashlib.md5()
    md5.update(param.encode('utf-8'))
    return md5.hexdigest()

def generate_token():
    temp = str(time.time()) + str(random.random())
    md5 = hashlib.md5()
    md5.update(temp.encode('utf-8'))
    return md5.hexdigest()


def register(request):
    if request.method == 'GET':
        return render(request, 'mine/register.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = generate_password(request.POST.get('password'))
        name = request.POST.get('name')

        user=User()
        user.email = email
        user.password = password
        user.name = name
        user.save()

        token = generate_token()
        cache.set(token, user.id, 60 * 60 * 24 * 3)

        request.session['token'] = token
    return render(request,'mine/mine.html')


def addcart(request):
    # 获取token
    token = request.session.get('token')

    # 响应数据
    response_data = {}

    # 缓存
    if token:
        userid = cache.get(token)
        # print(userid)    #获取用户id
        if userid:  # 已经登录
            user = User.objects.get(pk=userid)
            goodsid = request.GET.get('goodsid')
            goods = Goods.objects.get(pk=goodsid)
            # print(user,goodsid)  #点击商品后查看是否能获取对应id
            # 商品不存在: 添加新记录  商品存在: 修改number
            carts = Cart.objects.filter(user=user).filter(goods=goods)
            if carts.exists():
                cart = carts.first()
                cart.number = cart.number + 1
                cart.save()
            else:
                cart = Cart()
                cart.user = user
                cart.goods = goods
                cart.number = 1
                cart.save()

            response_data['status'] = 1  #添加成功
            response_data['number'] = cart.number
            response_data['msg'] = '添加 {} 购物车成功: {}'.format(cart.goods.productlongname, cart.number)

            return JsonResponse(response_data)
            # return HttpResponse('添加商品到购物车')
    response_data['status'] = -1   #未登录状态
    response_data['msg'] = '请登录后操作'
    return JsonResponse(response_data)

def checkemail(request):
    email = request.GET.get('email')

    # 去数据库中查找
    users = User.objects.filter(email=email)
    if users.exists():  # 账号被占用  1可用， 0不可用
        response_data = {
            'status': 0,
            'msg': '账号被占用!'
        }
    else:   # 账号可用
        response_data = {
            'status':1,
            'msg': '账号可用!'
        }
    return JsonResponse(response_data)

def subcart(request):
    goodsid = request.GET.get('goodsid')  #获取ajax请求参数
    goods = Goods.objects.get(pk=goodsid)   #通过商品id获取商品

    #用户  #减用户已经登录
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)

    #获取对应的购物车信息
    cart = Cart.objects.filter(user=user).filter(goods=goods).first()
    cart.number = cart.number -1
    cart.save()

    print((goodsid))
    response_data ={
        'msg':'删减成功',
        'status':1,
        'number':cart.number
    }
    return JsonResponse(response_data)

# def changecartselect(requset):
#     cartid = requset.GET.get('cartid')
#     print(cartid)
#     response_data = {
#         'msg':'状态修改成功',
#         'status':1,
#     }
#     return JsonResponse(response_data)
def changecartselect(request):
    cartid = request.GET.get('cartid')

    cart = Cart.objects.get(pk=cartid)
    cart.isselect = not cart.isselect
    cart.save()

    response_data = {
        'msg': '状态修改成功',
        'status': 1,
        'isselect': cart.isselect
    }

    return JsonResponse(response_data)

def changecartall(request):
    isall = request.GET.get('isall')

    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    carts = user.cart_set.all()

    if isall == 'true':
        isall = True
    else:
        isall = False

    for cart in carts:
        cart.isselect = isall
        cart.save()

    response_data = {
        'msg': '全选/取消全选 成功',
        'status': 1
    }

    return JsonResponse(response_data)

def generate_identifier():
    temp = str(time.time()) + str(random.randrange(1000,10000))
    return temp



def generateorder(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)

    # 订单
    order = Order()
    order.user = user
    order.identifier = generate_identifier()
    order.save()

    # 订单商品(购物车中选中)
    carts = user.cart_set.filter(isselect=True)
    for cart in carts:
        orderGoods = OrderGoods()
        orderGoods.order = order
        orderGoods.goods = cart.goods
        orderGoods.number = cart.number
        orderGoods.save()
        # 购买后从购物车中移除
        cart.delete()

    return render(request, 'order/orderdetail.html', context={'order': order})

def orderlist(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    orders = user.order_set.all()
    # status_list = ['未付款', '待发货', '待收货', '待评价', '已评价']
    return render(request, 'order/orderlist.html', context={'orders':orders})

def orderdetail(request, identifier):
    order = Order.objects.filter(identifier=identifier).first()
    return render(request, 'order/orderdetail.html', context={'order': order})

def returnurl(request):
    return redirect('axf:mine')


@csrf_exempt
def appnotifyurl(request):
    if request.method == 'POST':
        # 获取到参数
        body_str = request.body.decode('utf-8')
        # 通过parse_qs函数
        post_data = parse_qs(body_str)
        # 转换为字典
        post_dic = {}
        for k,v in post_data.items():
            post_dic[k] = v[0]
        # 获取订单号
        out_trade_no = post_dic['out_trade_no']
        # 更新状态
        Order.objects.filter(identifier=out_trade_no).update(status=1)
    return JsonResponse({'msg':'success'})


def pay(request):
    orderid = request.GET.get('orderid')
    order = Order.objects.get(pk=orderid)

    sum = 0
    for orderGoods in order.ordergoods_set.all():
        sum += orderGoods.goods.price * orderGoods.number

    # 支付地址信息
    data = alipay.direct_pay(
        subject='支付', # 显示标题
        out_trade_no=order.identifier,    #订单号
        total_amount=str(sum),   # 支付金额
        return_url='http://127.0.0.1:8000/axf/returnurl/'
    )

    # 支付地址
    alipay_url = 'https://openapi.alipaydev.com/gateway.do?{data}'.format(data=data)

    response_data = {
        'msg': '调用支付接口',
        'alipayurl': alipay_url,
        'status': 1
    }
    return JsonResponse(response_data)
