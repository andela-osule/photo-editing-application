angular.module('photoApp.controllers', [])
.controller('PhotosController', function($scope, $http, $rootScope, $timeout){
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
                .then(function(response) {
                    _this.photo.edited_at = response.data.edited_at;
                    $scope.messages = [response.data.messages];
                    $rootScope.ShowSublimalAlert();
                }, function(response) {
                    console.log('An error occurred');
                });
            }
            this.photo.title = photoTitle.val();
            photoTitle.prev().removeClass('hidden');
            photoTitle.addClass('hidden');
        }
    };
})
.controller('PhotoController', ['$scope', '$http', '$rootScope', 'Upload', function($scope, $http, $rootScope, Upload){
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