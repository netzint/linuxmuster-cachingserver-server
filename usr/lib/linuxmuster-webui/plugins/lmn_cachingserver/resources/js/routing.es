angular.module('lmn.cachingserver').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/cachingserver', {
        templateUrl: '/lmn_cachingserver:resources/partial/index.html',
        controller: 'Lmn_cachingserverIndexController',
    });
});
