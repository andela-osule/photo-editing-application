angular.module('photoApp', [])
    .config(function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    })
    .controller(
        'DownloadCtrl', function($scope, $http){
            $scope.UpdateDownloadCount =  function ($event, uri) {
                $http.get(uri).then(
                    function(data) {
                        $scope.downloadCount += 1;
                        return;
                    }
                );
            }
        })
 