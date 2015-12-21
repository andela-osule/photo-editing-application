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
                        //do something with it
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

//  $scope.fxCollection = response.fxCollection;