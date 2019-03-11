import hashlib
import random
import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from app.models import Wheel,Nav,Mustbuy,Shop,Mainshow,Foodtypes,Goods,User,Cart

# Create your views here.
from django_redis import cache
from django.core.cache import cache



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
        'foodtypes':foodtypes,
        'goods_list':goods_list,
        'childtype_list':childtype_list,
        'childid': childid,

    }

    return render(request,'market/market.html',context=response_dir)

def cart(request):
    return render(request,'cart/cart.html')

def mine(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = None
    if userid:
        user = User.objects.get(pk=userid)

    return render(request,'mine/mine.html',context={'user':user})

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

