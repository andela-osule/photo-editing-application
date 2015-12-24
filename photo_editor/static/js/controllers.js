angular.module('photoApp.controllers', [])
.controller('PhotosController',
    function ($scope, $http, $rootScope, $timeout) {
    /*
    |-------------------------------------------------------------
    | Set photos in controller scope
    |-------------------------------------------------------------
    */
        $http.get('/photos').success(
            function (responseData) {
                $scope.photos = responseData.photos;
            }
        );

        $rootScope.showSublimalAlert = function () {
            $timeout(function () {
                $scope.showAlert = true;
            }, 700);
            $timeout(function () {
                $scope.showAlert = false;
            }, 3500);
        };
         
        $rootScope.destroyAlert = function () {
            $scope.showAlert = false;
        };

        $scope.updatePhotoTitle = function ($event) {
            if ($event.which === 0 | $event.which == 13) {
                var photoId = this.photo.id;
                var photoTitle = angular.element($event.currentTarget);
                var scopeTitle = this.photo.title;
                var _this = this;
                if (photoTitle.val() != scopeTitle) {
                    angular.element('#loading').addClass('loading');
                    $http.post('/photo/'+photoId+'/update/', {title: photoTitle.val()})
                    .then(
                        function (response) {
                            angular.element('#loading').removeClass('loading');
                            _this.photo.edited_at = response.data.edited_at;
                            $scope.messages = [response.data.messages];
                            $rootScope.showSublimalAlert();
                        },
                        function (response) {
                            console.log('An error occurred');
                        }
                    );
                }
                this.photo.title = photoTitle.val();
                photoTitle.prev().removeClass('hidden');
                photoTitle.addClass('hidden');
            }
        };
    }
)
.controller('PhotoController', ['$scope', '$http', '$rootScope', 'Upload',
    function ($scope, $http, $rootScope, Upload) {
        $scope.upload = function ($files) {
            $scope.doUpload($files[0]);
        };
        $scope.doUpload = function ($file) {
            angular.element('#loading').addClass('loading');
            Upload.upload({
                url: '/upload/',
                data: {image: $file}
            })
            .then(
                function (response) {
                    angular.element('#loading').removeClass('loading');
                    $scope.$parent.messages = [response.data.messages];
                    $scope.$parent.photos.unshift(response.data.photo);
                    $rootScope.showSublimalAlert();
                },
                function (response) {
                    console.log('Error status: ' + response.status);
                },
                function (event) {
                    var progressPercentage = parseInt(100.0 * event.loaded / event.total);
                    $scope.$parent.messages = ['progress: ' + progressPercentage + '%'];
                }
            );
        };
    }
]);