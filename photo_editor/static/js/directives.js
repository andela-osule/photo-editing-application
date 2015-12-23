 angular.module('photoApp.directives', [])
 .directive('selectPhoto', ['$document', function ($document) {
    /*
    |-------------------------------------------------------------
    | Set directive to select each photo, handle when photo is clicked
    |-------------------------------------------------------------
    */
    return {
        restrict: 'A',
        templateUrl: 'static/Partials/selection.html',
        link: function (scope, element, attr) {
            element.on('click', function (event) {
                event.preventDefault();
                angular.element('.selected').toggleClass('selected');
                angular.element(this).toggleClass('selected');
                angular.element('#photo').attr({
                    'src':angular.element(this).attr('data-filesrc')
                });
            });
        }
    };
}])
.directive('deletePhoto', ['$document', '$http', '$rootScope', function($document, $http, $rootScope) {
    /*
    |-------------------------------------------------------------
    | Set directive to delete a selected photo
    |-------------------------------------------------------------
    */   
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.on('click', function (event) {
                event.preventDefault();
                var selectedPhoto = angular.element('.selected');
                var photoId = selectedPhoto.attr('data-id');
                if(photoId === undefined){
                    scope.messages = [{'tags':'info', 'text':'Select a photo to delete'}];
                }
                else {
                    $http.get('/photo/'+photoId+'/delete').success(
                        function (responseData) {
                            scope.messages = responseData;
                            $rootScope.ShowSublimalAlert();
                            scope.photos.splice(scope.photos.indexOf(scope.photos), 1 );
                                console.log(scope.photos);
                        }
                    );
                    angular.element('#photo').removeAttr('src').hide();
                }
            });
        }
    };
}])
.directive('editPhoto', ['$http', 'EffectsDS', function ($http, $EffectsDS) {
    /*
    |-------------------------------------------------------------
    | Set directive to edit a selected photo
    |-------------------------------------------------------------
    */
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.on('click', function (event) {
                event.preventDefault();
                var selectedPhoto = angular.element('.selected');
                var photoId = selectedPhoto.attr('data-id');
                if(photoId === undefined) {
                    scope.$apply(function() {
                        scope.messages = [{'tags':'info', 'text':'Select a photo to edit'}];
                        scope.ShowSublimalAlert();
                    });
                }
                else {
                    scope.$apply(function () {
                        //scope.fxCollection = $EffectsDS.getEffects();
                        $EffectsDS.getEffects().then(function (data) {
                            scope.effectList  = data;
                            scope.effectIsLoaded = $EffectsDS.getStatus();
                        });
                    });
                }
            });
        }
    };
}])
.directive('editPhotoTitle', ['$http', function ($http) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.on('click', function (event, $http) {
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
.directive('fxApply', ['$http', function ($http) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.on('click', function () {
                if(angular.element(this).hasClass('active')){
                    return;
                } else {
                    angular.element('.effect').removeClass('active');
                    angular.element(this).addClass('active');
                }
                var photoId = angular.element('.selected').attr('data-id');
                $http.get('/photo/'+ photoId + '/fx/' + scope.effect.name + '/').success(
                    function (response) {
                        angular.element('#photo').attr({'src':response.filteredPhotoURI}).show();
                    }
                );
            });
        }
    };
}])
.directive('sharePhoto', ['$http', 'Publish', function ($http, Publish) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.on('click', function () {
                var transformPhotoSrc = angular.element('#photo').attr('src');
                if (transformPhotoSrc !== undefined){
                    $http.post('/photo/share/', {src:transformPhotoSrc})
                    .success(
                        function(response) {
                            if(response.status) {
                                var name = angular.element('.selected span.img-title').text();
                                Publish.do(name, response.uri, response.photo, response.APP_ID).then(
                                    function (data) {
                                        scope.messages = [{'tags':'info', 'text':'Photo URI has been shared to your timeline.'}];
                                        scope.ShowSublimalAlert();
                                    },
                                    function (data) {
                                        scope.messages = [{'tags':'danger', 'text':'Photo URI couldn\'t be shared to your timeline.'}];
                                        scope.ShowSublimalAlert();
                                    }
                                );
                            }
                        }
                    ).error(function (response) {
                        scope.messages = [{'tags':'danger', 'text':'An error occurred.'}];
                        scope.ShowSublimalAlert();
                    });
                }
            });
        }
    };
}]);