'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.cachingserver', ['core']);


'use strict';

angular.module('lmn.cachingserver').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/cachingserver', {
        templateUrl: '/lmn_cachingserver:resources/partial/index.html',
        controller: 'Lmn_cachingserverIndexController'
    });
});


'use strict';

angular.module('lmn.cachingserver').controller('Lmn_cachingserverIndexController', function ($scope, $http, $uibModal, pageTitle, gettext, notify) {

    pageTitle.set(gettext('Cachingserver Manager'));

    $scope.start = function () {
        $http.get('/api/lmn/cachingserver/isinstalled').then(function (resp) {
            $scope.isinstalled = resp.data;
            if ($scope.isinstalled) {
                $scope.getServer();
            }
        });
    };

    $scope.getServer = function () {
        $http.get('/api/lmn/cachingserver/getserver').then(function (resp) {
            $scope.server = resp.data;
            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                var _loop = function _loop() {
                    var server = _step.value;

                    console.log(server);
                    $http.post('/api/lmn/cachingserver/server-status', { server: server["ip"] }).then(function (resp) {
                        server["status"] = resp.data.status;
                    });
                    $http.post('/api/lmn/cachingserver/configuration-status', { server: server["ip"] }).then(function (resp) {
                        server["configurationstatus"] = resp.data.data.status;
                    });
                    $http.post('/api/lmn/cachingserver/images-status', { server: server["ip"] }).then(function (resp) {
                        server["imagesstatus"] = resp.data.data.status;
                    });
                };

                for (var _iterator = $scope.server[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    _loop();
                }
            } catch (err) {
                _didIteratorError = true;
                _iteratorError = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion && _iterator.return) {
                        _iterator.return();
                    }
                } finally {
                    if (_didIteratorError) {
                        throw _iteratorError;
                    }
                }
            }
        });
    };

    $scope.getImages = function () {
        $http.get('/api/lmn/cachingserver/getimages').then(function (resp) {
            $scope.images = resp.data.data;
        });
    };

    $scope.toggleImageForServer = function (currentStatus, server, imagename) {
        if (!currentStatus) {
            // add image to server
            $http.post('/api/lmn/cachingserver/addimagetoserver', { server: server, imagename: imagename }).then(function (resp) {
                notify.success(gettext("Image added successfully!"));
            });
        } else {
            // remove image from server
            $http.post('/api/lmn/cachingserver/removeimagefromserver', { server: server, imagename: imagename }).then(function (resp) {
                notify.success(gettext("Image removed successfully!"));
            });
        }
        $scope.getServer();
    };

    $scope.syncConfiguration = function (server) {
        $http.post('/api/lmn/cachingserver/configuration-sync', { server: server }).then(function (resp) {
            if (resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            } else {
                notify.error(gettext('Failed to initiate sync!'));
                console.log("Error: " + resp.data.data);
            }
        });
    };

    $scope.syncImages = function (server) {
        $http.post('/api/lmn/cachingserver/images-sync', { server: server }).then(function (resp) {
            if (resp.data.status) {
                notify.success(gettext('Sync initiated successfully!'));
            } else {
                notify.error(gettext('Failed to initiate sync!'));
                console.log("Error: " + resp.data.data);
            }
        });
    };

    $scope.getLogs = function (server) {
        $uibModal.open({
            templateUrl: '/lmn_cachingserver:resources/partial/logs.modal.html',
            controller: 'Lmn_cachingserverLogsModalController',
            size: 'lg',
            resolve: {
                server: function (_server) {
                    function server() {
                        return _server.apply(this, arguments);
                    }

                    server.toString = function () {
                        return _server.toString();
                    };

                    return server;
                }(function () {
                    return server;
                })
            }
        }).result.then(function (result) {
            $scope.getServer();
        });
    };

    $scope.$watch('identity.user', function () {
        if ($scope.identity.user == undefined) {
            return;
        }
        if ($scope.identity.user == null) {
            return;
        }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });
});

angular.module('lmn.cachingserver').controller('Lmn_cachingserverLogsModalController', function ($scope, $http, $timeout, $interval, pageTitle, gettext, notify, $uibModalInstance, server) {

    $scope.server = server;

    $scope.loadLogs = function () {
        $http.post('/api/lmn/cachingserver/logs', { server: server }).then(function (resp) {
            console.log(resp);
            if (resp.data.status) {
                $scope.logs = resp.data.data.data;
            } else {
                console.log("Error: " + resp.data.data);
            }
            $timeout(function () {
                var element = document.getElementById('logPre');
                element.scrollTop = element.scrollHeight;
            }, 0);
        });
    };

    $scope.close = function () {
        $interval.cancel(loginterval);
        $uibModalInstance.close();
    };

    $scope.loadLogs();
    var loginterval = $interval($scope.loadLogs, 1000);
});


