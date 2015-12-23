angular.module('photoApp',
    [
        'angularMoment',
        'slickCarousel',
        'photoEffectsSvc',
        'ngFileUpload',
        'ngAnimate',
        'photoApp.directives',
        'photoApp.controllers'
    ]
)
.config(
    ['$interpolateProvider', 'slickCarouselConfig', function($interpolateProvider, slickCarouselConfig){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
        slickCarouselConfig.dots = false;
        slickCarouselConfig.autoplay = false;
    }]
)
    
   
