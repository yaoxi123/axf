$(function () {
        var swiper = new Swiper('#topSwiper', {
        pagination: '.swiper-pagination',
        slidesPerView: 1,
        paginationClickable: true,
        spaceBetween: 30,
        loop: true,
        autoplay:3000,
    });

        var swiper = new Swiper('#mustbuySwiper', {
        pagination: '.swiper-pagination',
        slidesPerView: 3,
        paginationClickable: true,
        spaceBetween: 5,
        autoplay:3000,
    });
})