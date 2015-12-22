angular.module('photoApp', ['angularMoment', 'slickCarousel', 'PhotoEffectsSvc', 'ngFileUpload', 'ngAnimate'])
    .config(function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    })
    .config(
        ['slickCarouselConfig', function(slickCarouselConfig){
            slickCarouselConfig.dots = false;
            slickCarouselConfig.autoplay = false;
        }]
    )
    .controller(
        'PhotosCtrl', function($scope, $http, $rootScope, $timeout){
/*
|-------------------------------------------------------------
| Set photos in controller scope
|-------------------------------------------------------------
*/
        $http.get('/photos').success(
            function(responseData) {
                $scope.photos = responseData.photos;
            }
        );
        $rootScope.ShowSublimalAlert = function(){
            $timeout(function(){
                $scope.showAlert = true;
            }, 700);
            $timeout(function(){
                $scope.showAlert = false;
            }, 3500);
        };
        $rootScope.DestroyAlert = function() {
              $scope.showAlert = false;
        };
        $scope.UpdatePhotoTitle = function($event) {
            if($event.which === 0 | $event.which == 13)
            {
                var photoId = this.photo.id;
                var photoTitle = angular.element($event.currentTarget);
                var scopeTitle = this.photo.title;
                var _this = this;
                if(photoTitle.val() != scopeTitle) {
                $http.post('/photo/'+photoId+'/update/', {title: photoTitle.val()})
                .then(function(response){
                    _this.photo.edited_at = response.data.edited_at;
                    $scope.messages = [response.data.messages];
                    $rootScope.ShowSublimalAlert();
                }, function(response){
                    console.log('An error occurred');
                });
                }
                this.photo.title = photoTitle.val();
                photoTitle.prev().removeClass('hidden');
                photoTitle.addClass('hidden');
            }
        };
    }).controller(
        'PhotoCtrl', ['$scope', '$http', '$rootScope', 'Upload', function($scope, $http, $rootScope, Upload){
            $scope.upload = function ($files) {
                $scope.doUpload($files[0]);
            };
            $scope.doUpload = function($file) {
                Upload.upload({
                url: '/upload/',
                data: {image: $file}
                }).then(function (response) {
                    $scope.$parent.messages = [response.data.messages];
                    $scope.$parent.photos.unshift(response.data.photo);
                    $rootScope.ShowSublimalAlert();
                }, function (response) {
                    console.log('Error status: ' + response.status);
                }, function (event) {
                    var progressPercentage = parseInt(100.0 * event.loaded / event.total);
                    $scope.$parent.messages = ['progress: ' + progressPercentage + '%'];
                });
            };
    }])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to select each photo, handle when photo is clicked
|-------------------------------------------------------------
*/
        'selectPhoto', ['$document', function($document) {
            return {
                restrict: 'A',
                templateUrl: 'static/Partials/selection.html',
                link: function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        angular.element('.selected').toggleClass('selected');
                        angular.element(this).toggleClass('selected');
                        angular.element('#photo').attr({'src':angular.element(this).attr('data-filesrc')});
                    });
                }
            };
    }])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to delete a selected photo
|-------------------------------------------------------------
*/
        'deletePhoto', ['$document', '$http', '$rootScope', function($document, $http, $rootScope) {
            return {
                restrict: 'A',
                link: function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        var selectedPhoto = $('.selected');
                        var photoId = selectedPhoto.attr('data-id');
                        if(photoId === undefined){
                            scope.messages = [{'tags':'info', 'text':'Select a photo to delete'}];
                        }
                        else {
                            selectedPhoto.remove();
                            $http.get('/photo/'+photoId+'/delete').success(
                                function(responseData){
                                    scope.messages = responseData;
                                    $rootScope.ShowSublimalAlert();
                                }
                            );
                            angular.element('#photo').removeAttr('src').hide();
                        }
                    });
                }
            };
        }])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to edit a selected photo
|-------------------------------------------------------------
*/
        'editPhoto', ['$http', 'EffectsDS', function ($http, $EffectsDS) {
            return {
                restrict: 'A',
                link:function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        var selectedPhoto = angular.element('.selected');
                        var photoId = selectedPhoto.attr('data-id');
                        if(photoId === undefined){
                            scope.$apply(function(){
                                scope.messages = [{'tags':'info', 'text':'Select a photo to edit'}];
                                scope.ShowSublimalAlert();
                            });
                        }
                        else {
                            scope.$apply(function(){
                                //scope.fxCollection = $EffectsDS.getEffects();
                                $EffectsDS.getEffects().then(function(data)
                                    {
                                        scope.effectList  = data;
                                        scope.effectIsLoaded = $EffectsDS.getStatus();
                                    });
                            });
                        }
                    });
                }
            };
        }])
    .directive(
        'editPhotoTitle', ['$http', function ($http) {
            return {
                restrict: 'A',
                link: function (scope, element, attr) {
                    element.on('click', function (event, $http){
                            var input = angular.element(this).next();
                            input.toggleClass('hidden').focus();
                            var oldValue = input.val();
                            input.val('');
                            input.val(oldValue);
                            angular.element(this).toggleClass('hidden');
                    });
                }
            };
        }])
    .directive(
        'fxApply', ['$http', function ($http){
            return {
                restrict: 'A',
                link: function(scope, element, attr) {
                    element.on('click', function (){
                        var photoId = angular.element('.selected').attr('data-id');
                        $http.get('/photo/'+ photoId + '/fx/' + scope.effect.name + '/').success(
                            function(response){
                                angular.element('#photo').attr({'src':response.fxSrc}).show();
                            }
                        );
                    });
                }
            };
        }])
    .directive(
        'sharePhoto', ['$http', 'Publish', function($http, Publish){
            return {
                restrict: 'A',
                link: function(scope, element, attr) {
                    element.on('click', function() {
                        var transformPhotoSrc = angular.element('#photo').attr('src');
                        if (transformPhotoSrc !== undefined){
                            $http.post('/photo/share/', {src:transformPhotoSrc})
                            .success(
                                function(response){
                                    if(response.status) {
                                        var name = angular.element('.selected span.img-title').text();
                                        Publish.do(name, response.uri, response.photo, response.APP_ID).then(
                                            function(data){
                                                scope.messages = [{'tags':'info', 'text':'Photo URI has been shared to your timeline.'}];
                                                scope.ShowSublimalAlert();
                                            },
                                            function(data){
                                                scope.messages = [{'tags':'danger', 'text':'Photo URI couldn\'t be shared to your timeline.'}];
                                                scope.ShowSublimalAlert();
                                            }
                                        );
                                    }
                                }
                            ).error(function(response){
                                scope.messages = [{'tags':'danger', 'text':'An error occurred.'}];
                                scope.ShowSublimalAlert();
                            });
                        }
                    });
                }
            };

        }]);
