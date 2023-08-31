angular.module('lmn.cachingserver').controller('Lmn_cachingserverIndexController', function($scope, $http, pageTitle, gettext, notify) {

    $scope.start = () => {
        $http.get('/api/lmn/cachingserver/isinstalled').then( (resp) => {
            $scope.isinstalled = resp.data;
            if($scope.isinstalled) {
                $scope.getServer();
                $scope.getServerFileHashes();
            }
        });
    }

    $scope.getServer = () => {
        $http.get('/api/lmn/cachingserver/getserver').then( (resp) => {
            $scope.server = resp.data;
            for(let server in $scope.server) {
                $http.post('/api/lmn/cachingserver/server-status', {server: $scope.server[server]["ip"]}).then( (resp) => {
                    $scope.server[server]["status"] =  resp.data.status;
                });
                $http.post('/api/lmn/cachingserver/file-status', {server: $scope.server[server]["ip"]}).then( (resp) => {
                    $scope.server[server]["filestatus"] =  resp.data.data;
                });
            }
        });
    }

    $scope.getImages = () => {
        $http.get('/api/lmn/cachingserver/getimages').then( (resp) => {
            $scope.images = resp.data.data;
        });
    }

    $scope.syncServer = (servername, syncitem) => {
        $http.post('/api/lmn/cachingserver/syncserver', {servername: servername, syncitem: syncitem}).then( (resp) => {
            if(resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            }
            else {
                notify.error(gettext('Failed to initiate sync!'));
            }
        });
    }

    $scope.getServerFileHashes = () => {
        $http.get('/api/lmn/cachingserver/getserverfilehashed').then( (resp) => {
            $scope.serverfilehashes = resp.data;
        });
    }

    $scope.$watch('identity.user', function() {
        if ($scope.identity.user == undefined) { return; }
        if ($scope.identity.user == null) { return; }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });

});

