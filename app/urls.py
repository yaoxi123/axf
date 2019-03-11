from django.conf.urls import url
from app import views


urlpatterns = [
    url(r'^$',views.home,name='home'),   #首页
    # url(r'^market/$',views.market,name='marketbase'),
    # url(r'^market/(\d+)/$',views.market,name='market'),   #闪购
    url(r'^market/$',views.market,name='marketbase'),
    url(r'^market/(?P<childid>\d+)/(?P<sortid>\d+)/$',views.market,name='market'),
    # url(r'^market/(?P<childid>\d+)/(?P<sortid>\d+)/$', views.market, name='market'), # 闪购超市
    url(r'^cart/$',views.cart,name='cart'),   #购物车
    url(r'^mine/$',views.mine,name='mine'),   #我的
    url(r'^login/$',views.login,name='login'),   #登陆
    url(r'^logout/$', views.logout, name='logout'),  # 注销
    url(r'^register/$', views.register, name='register'),  # 注册
    url(r'^addcart/$', views.addcart, name='addcart'),  # 添加到购物车
    ]