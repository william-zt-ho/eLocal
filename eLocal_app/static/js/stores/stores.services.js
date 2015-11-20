(function () {
  'use strict';

  angular
    .module('Store')
    .factory('StoreService', StoreService);

  StoreService.$inject = ['$http', 'API_SERVER'];

  function StoreService ($http, API_SERVER) {
    var service = {};

    service.getMerchantStores = function (merchant_id) {
      return $http.get(API_SERVER + 'api/users/' + merchant_id + '/stores/');
    };

    service.createStore = function (merchant_id, data) {
      return $http.post(API_SERVER + 'api/users/' + merchant_id + '/stores/', data);
    };

    return service;
  }
})();
