angular.module('photoApp', ['angularMoment'])
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
                    $scope.photos = JSON.parse(responseData);
                }
            );
    })
    .directive(
/*
|-------------------------------------------------------------
| Set directive for each photo, handle when photo is clicked
|-------------------------------------------------------------
*/
        'selectImg', ['$document', function($document) {
            return {
                link: function (scope, element, attr) {
                    element.on('click', function(event){
                        event.preventDefault();
                        $('.selected').toggleClass('selected');
                        element.toggleClass('selected');
                    });
                }
            }
    }]);
