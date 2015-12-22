//Services Module
var app = angular.module('PhotoEffectsSvc', []);
// Service definition
app.service('EffectsDS', function($http){
    var effectIsLoaded = false;

    var photos = [];

    var effects = [];

    return {
        setTrue: function(){
            effectIsLoaded = true;
        },
        setFalse: function(){
            effectIsLoaded = false;
        },

        getStatus: function(){
            return effectIsLoaded;
        },

        getEffects: function() {
            var _this = this;
            if (effects.length === 0){
                return $http.get('/settings/effects/').then(
                    function(response){
                        Array.prototype.push.apply(effects, response.data.fxCollection);
                        _this.setTrue();
                        return effects;
                    },
                    function(response)
                    {
                        console.log('An error occurred');
                    },
                    function(event){
                        _this.setFalse();
                    }
                );
            }
            return effects;
        }
    };    
});

app.service('Publish', function($q){
     return {
        do: function(name, uri, img, app_id){
            var deferred = $q.defer();
            FB.init({
                appId: app_id,
                status: true,
                cookie: true,
                xfbml: true,
                version: 'v2.4'
            });
            FB.ui({
              method: 'feed',
              name: name,
              display: 'popup',
              link: location.protocol + '//' + location.host + '/photo/share?uri=' + uri,
              caption:"Shared from Photo Editr",
              picture: "http://" + location.host + '/' + encodeURIComponent(img),
              description: 'Check me out on Photo Editr - Built with <3 by CodeKnight'
            }, function(response){
                if (!response || response.error) {
                    deferred.reject('Error occured');
                } else {
                    deferred.resolve(response);
                }
            });
            return deferred.promise;
        }
    }
})
