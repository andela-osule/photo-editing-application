angular.module('photoApp', ['angularMoment', 'ngFileUpload', 'ngAnimate'])
    .config(function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    })
    .controller(
        'PhotosCtrl', function($scope, $http){
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
        $scope.DestroyAlert = function() {
            $('.alert').addClass('hide');
        }
        $scope.UpdatePhotoTitle = function($event) {
            if($event.which == 0 | $event.which == 13)
            {
                var photoId = this.photo.id;
                var photoTitle = $($event.currentTarget);
                var scopeTitle = this.photo.title;
                var _this = this;
                if(photoTitle.val() != scopeTitle) {
                $http.post('/photo/'+photoId+'/update/', {title: photoTitle.val()})
                .then(function(response){
                    console.log(response.data.messages);
                    _this.photo.edited_at = response.data.edited_at;
                    $scope.messages = [response.data.messages];
                }, function(response){
                    console.log('An error occurred');
                });
                }
                this.photo.title = photoTitle.val();
                photoTitle.prev().removeClass('hidden');
                photoTitle.addClass('hidden');
            }
        }
    }).controller(
        'PhotoCtrl', ['$scope', '$http', 'Upload', function($scope, $http, Upload){
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
                    $scope.$parent.DestroyAlert();
                }, function (response) {
                    console.log('Error status: ' + response.status);
                }, function (event) {
                    var progressPercentage = parseInt(100.0 * event.loaded / event.total);
                    console.log('progress: ' + progressPercentage + '% ');
                });
            };
        }
    ])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to select each photo, handle when photo is clicked
|-------------------------------------------------------------
*/
        'selectPhoto', ['$document', function($document) {
            return {
                templateUrl: 'static/Partials/selection.html',
                link: function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        $('.selected').toggleClass('selected');
                        $(this).toggleClass('selected');
                        $('#photo').attr({'src':$(this).attr('data-filesrc')});
                    });
                }
            }
    }])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to delete a selected photo
|-------------------------------------------------------------
*/
        'deletePhoto', ['$document', '$http', function($document, $http) {
            return function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        var selectedPhoto = $('.selected');
                        var photoId = selectedPhoto.attr('data-id');
                        if(photoId == undefined){
                            scope.messages = [{'tags':'info', 'text':'Select a photo to delete'}];
                            scope.$apply();
                        }
                        else {
                            selectedPhoto.remove();
                            $http.get('/photo/'+photoId+'/delete').success(
                                function(responseData){
                                    scope.messages = responseData;
                                    scope.DestroyAlert();
                                }
                            );
                        }
                    });
                }
        }])
    .directive(
/*
|-------------------------------------------------------------
| Set directive to edit a selected photo
|-------------------------------------------------------------
*/
        'editPhoto', ['$document', '$http', function ($document, $http) {
            return function (scope, element, attr) {
                element.on('click', function(event){
                    event.preventDefault();
                    var selectedPhoto = $('.selected');
                    var photoId = selectedPhoto.attr('data-id');
                    if(photoId == undefined){
                        scope.messages = [{'tags':'info', 'text':'Select a photo to edit'}];
                        scope.$apply();
                    }
                    else {
                    }
                });
            }
        }])
    .directive(
        'editPhotoTitle', ['$document', '$http', '$compile', function ($document, $compile, $http) {
            return function (scope, element, attr) {
                element.on('click', function (event, $http){
                        var input = $(this).next();
                        input.toggleClass('hidden').focus();
                        var oldValue = input.val();
                        input.val('');
                        input.val(oldValue);
                        $(this).toggleClass('hidden');
                });
            }
        }]);
