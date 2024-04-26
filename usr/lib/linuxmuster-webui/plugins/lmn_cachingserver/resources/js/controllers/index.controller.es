angular.module('lmn.cachingserver').controller('Lmn_cachingserverIndexController', function($scope, $http, $uibModal, pageTitle, gettext, notify) {

    $scope.start = () => {
        $http.get('/api/lmn/cachingserver/isinstalled').then( (resp) => {
            $scope.isinstalled = resp.data;
            if($scope.isinstalled) {
                $scope.getServer();
            }
        });
    }

    $scope.getServer = () => {
        $http.get('/api/lmn/cachingserver/getserver').then( (resp) => {
            $scope.server = resp.data;
            for(let server of $scope.server) {
                console.log(server)
                $http.post('/api/lmn/cachingserver/server-status', {server: server["ip"]}).then( (resp) => {
                    server["status"] =  resp.data.status;
                });
                $http.post('/api/lmn/cachingserver/configuration-status', {server: server["ip"]}).then( (resp) => {
                    server["configurationstatus"] =  resp.data.data.status;
                });
                $http.post('/api/lmn/cachingserver/images-status', {server: server["ip"]}).then( (resp) => {
                    server["imagesstatus"] =  resp.data.data.status;
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

    $scope.syncConfiguration = (server) => {
        $http.post('/api/lmn/cachingserver/configuration-sync', {server: server}).then( (resp) => {
            if(resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            }
            else {
                notify.error(gettext('Failed to initiate sync!'));
                console.log("Error: " + resp.data.data)
            }
        });
    }

    $scope.syncImages = (server) => {
        $http.post('/api/lmn/cachingserver/images-sync', {server: server}).then( (resp) => {
            if(resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            }
            else {
                notify.error(gettext('Failed to initiate sync!'));
                console.log("Error: " + resp.data.data)
            }
        });
    }

    $scope.getLogs = (server) => {
        $uibModal.open({
            templateUrl: '/lmn_cachingserver:resources/partial/logs.modal.html',
            controller: 'Lmn_cachingserverLogsModalController',
            size: 'lg',
            resolve: {
                server: function () {
                    return server
                }
            }
        }).result.then((result) => {
            $scope.getServer();
        });
    }

    $scope.$watch('identity.user', function() {
        if ($scope.identity.user == undefined) { return; }
        if ($scope.identity.user == null) { return; }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });

});

angular.module('lmn.cachingserver').controller('Lmn_cachingserverLogsModalController', function($scope, $http, $timeout, $interval, pageTitle, gettext, notify, $uibModalInstance, server) {
    
    $scope.server = server;
    
    $scope.loadLogs = () => {
        $http.post('/api/lmn/cachingserver/logs', {server: server}).then( (resp) => {
            console.log(resp)
            if(resp.data.status) {
                $scope.logs = resp.data.data.data;
            }
            else {
                console.log("Error: " + resp.data.data);
            }
            $timeout(function() {
                var element = document.getElementById('logPre');
                element.scrollTop = element.scrollHeight;
            }, 0);
        });
    }

    $scope.close = () => {
        $interval.cancel(loginterval);
        $uibModalInstance.close();
    }

    $scope.loadLogs();
    var loginterval = $interval($scope.loadLogs, 1000);
});