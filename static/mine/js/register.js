$(function () {
    $('.register').width(innerWidth)

    //邮箱验证 格式是否正确  是否可用
    $('#email input'.blur(function () {
        var reg = new RegExp("^[a-z0-9]+([._\\-]*[a-z0-9])*@([a-z0-9]+[-a-z0-9]*[a-z0-9]+.){1,63}[a-z0-9]+$");
        if ($(this).val() == '')return
        if (reg.test($this).val()){

        }else{

        }

    }))
})