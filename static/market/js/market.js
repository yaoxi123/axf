$(function () {
    //jquery.cookie 用法
    //$.cookie(key ,value ,arg) 设置cookie
    //value = $.cookie(key)获取
    //$.cookie(key,null)删除

    // var index = localStorage.getItem('index')  //未设置cookie时index获取方式
    var index = $.cookie('index')

    // 获取点击（this记录的index）
    console.log(index)
    if (index){ // 有点击，有下标
    $('.type-slider li').eq(index).addClass('active');
} else {
    $('.type-slider li:first').addClass('active')
}

    // $('.type-slider li').eq(index).addClass('active')   //点击a标签页面更新后添加class=active（此时问题：页面退出后从其它页面再进入该页面还是显示之前点击的标签显示黄色，商品跟对应显示分类不匹配）（解决问题：客户端之前点击的是哪个分类  可以根据index 获取对应的商品分类id）
    //客户端（浏览器）：存储localStorage(index) 通过localStorage获取index传递给服务器（通过cookie）存储
    //cookie存在客户端，请求的时候会自动携带本域名下的index
    //服务其从cookie获取index(此时不需要传递categoryid参数)

    //侧边栏分类点击时添加active功能
    //获取class=type-slider 下的li标签添加点击事件
    $('.type-slider li').click(function () {
        //$（this）  当前点击的时候对象添加addClass
        // $(this).addClass('active')  //此时添加只有点击鼠标时才显示黄色标签   松开鼠标后消失（由于点击a标签更新页面）

        //点击后记录下标，(this)点击记录（index)
        // localStorage.setItem('index',$(this).index())
        //localstorage浏览器记录
         $.cookie('index',$(this).index(),{expires:3,path:'/'})
        //expires:3 有效期三天
        //path:'/'路径
    })

    //分类点击（全部类型）
    var categoryShow = false
    $('#category-bt').click(function () {
        // console.log(categoryShow)
        // if (categoryShow){   //隐藏
        //      categoryShow = false
        //     $('.category-view').hide()
        // } else {
        //     categoryShow = true
        //     $('.category-view').show()
        // }
        categoryShow = !categoryShow
        categoryShow ? categoryViewShow() : categoryViewHide()
    })

    function  categoryViewShow() {
        $('.category-view').show()
        $('#category-bt i').removeClass('glyphicon glyphicon-chevron-up').addClass('glyphicon glyphicon-chevron-down')
        sortViewHide()
        sortShow = false
    }
    function  categoryViewHide() {
        $('.category-view').hide()
        $('#category-bt i').removeClass('glyphicon glyphicon-chevron-down').addClass('glyphicon glyphicon-chevron-up')

    }

    //排序
    var sortShow = false
    $('#sort-bt').click(function () {
        sortShow = !sortShow
        sortShow ? sortViewShow() : sortViewHide()
    })

    function sortViewShow() {
        $('.sort-view').show()
        $('#sort-bt i').removeClass('glyphicon glyphicon-chevron-up').addClass('glyphicon glyphicon-chevron-down')
        categoryViewHide()
        categoryShow = false
    }
    function  sortViewHide() {
        $('.sort-view').hide()
        $('#sort-bt i').removeClass('glyphicon glyphicon-chevron-down').addClass('glyphicon glyphicon-chevron-up')

    }
    
    //灰色蒙层
    $('.bounce-view').click(function () {
         sortViewHide()
        sortShow = false

        categoryViewHide()
        categoryShow = false
    })
    //隐藏(减号跟商品数量)
    $('.bt-wrapper>.glyphicon-minus').hide()
    $('.bt-wrapper>i').hide()

    //点击加号添加操作事件
    $('.bt-wrapper>.glyphicon-plus').click(function () {
       console.log('点击+')   //验证点击是否可以触发
        //添加购物车需要传递用户跟商品，（需先登陆）
        //请求数据  每个按钮身上都对应的商品id属性
         request_data = {
            'goodsid': $(this).attr('data-goodsid')
        }

        $.get('/axf/addcart/', request_data, function (response) {
            console.log(response)

            if (response.status == -1){ // 未登录

                // 设置cookie
                $.cookie('back', 'market', {expires: 3, path: '/'})

                window.open('/axf/login/', '_self')


            }
        })
    })

})

//