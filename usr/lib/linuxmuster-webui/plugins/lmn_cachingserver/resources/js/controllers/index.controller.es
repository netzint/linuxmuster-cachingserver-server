angular.module('lmn.cachingserver').controller('Lmn_cachingserverIndexController', function($scope, $http, pageTitle, gettext, notify) {

    $scope.start = () => {
        $http.get('/api/lmn/cachingserver/isinstalled').then( (resp) => {
            $scope.isinstalled = resp.data;
            if($scope.isinstalled) {
                $scope.getServer();
            }
        });
    }

    $scope.getServer = () => {
        $scope.getServerFileHashes();
        $http.get('/api/lmn/cachingserver/getserver').then( (resp) => {
            $scope.server = resp.data;
            for(let server in $scope.server) {
                $http.post('/api/lmn/cachingserver/server-status', {server: $scope.server[server]["ip"]}).then( (resp) => {
                    $scope.server[server]["status"] =  resp.data.status;
                });
                $http.post('/api/lmn/cachingserver/file-status', {server: $scope.server[server]["ip"], images: $scope.server[server]["images"]}).then( (resp) => {
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

    $scope.toggleImageForServer = (currentStatus, server, imagename) => {
        console.log(currentStatus)
        if (!currentStatus) {
            // add image to server
            $http.post('/api/lmn/cachingserver/addimagetoserver', {server: server, imagename: imagename}).then( (resp) => {
                notify.success(gettext("Image added successfully!"))
            });
        }
        else {
            // remove image from server
            $http.post('/api/lmn/cachingserver/removeimagefromserver', {server: server, imagename: imagename}).then( (resp) => {
                notify.success(gettext("Image removed successfully!"))
            });
        }
        $scope.getServer();
    }

    $scope.syncFiles = (server, item) => {
        $http.post('/api/lmn/cachingserver/file-sync', {server: server, item: item}).then( (resp) => {
            if(resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            }
            else {
                notify.error(gettext('Failed to initiate sync!'));
                console.log("Error: " + resp.data.data)
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

