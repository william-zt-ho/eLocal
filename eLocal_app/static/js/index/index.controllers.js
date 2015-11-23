(function () {
  'use strict';

  angular.module('Index')

  .controller('IndexNavController', IndexNavController)
  .controller('IndexStoreController', IndexStoreController)
  .controller('IndexProductController', IndexProductController)
  .controller('IndexSingleStoreController', IndexSingleStoreController)
  .controller('IndexCartController', IndexCartController)
  .controller('IndexEditProductController', IndexEditProductController);

  IndexNavController.$inject = ['$scope', '$window', '$state'];

  function IndexNavController ($scope, $window, $state) {
    $scope.zipcode = $window.localStorage.zipcode;
    $scope.radius = $window.localStorage.radius;
  }

  IndexStoreController.$inject = ['$scope', '$window', '$state', 'ngToast', 'StoreService', '$uibModal'];

  function IndexStoreController ($scope, $window, $state, ngToast, StoreService, $uibModal) {
    var zipcode = $window.localStorage.zipcode;
    var lat = $window.localStorage.lat;
    var lng = $window.localStorage.lng;
    var radius = $window.localStorage.radius;

    function getZipcodeStores () {
      StoreService.getZipcodeStores({'lat': lat, 'lng': lng, 'radius': radius}).then(
        function (response) {
          $scope.stores = response.data;
          $scope.displayedStores = [].concat($scope.stores);
        },
        function (response) {
          ngToast.danger({
            content: "Error while loading stores",
            dismissButton: true
          });
        }
      );
    }
    getZipcodeStores();
  }

  IndexProductController.$inject = ['$scope', '$window', '$state', '$uibModal', 'ngToast', 'StoreService'];

  function IndexProductController ($scope, $window, $state, $uibModal, ngToast, StoreService) {
    var zipcode = $window.localStorage.zipcode;
    var lat = $window.localStorage.lat;
    var lng = $window.localStorage.lng;
    var radius = $window.localStorage.radius;

    $scope.editProduct = function (product) {
      var index = $scope.products.indexOf(product);
      if (index !== -1) {
        var editProductModal = $uibModal.open({
          animation: true,
          templateUrl: '/static/js/modals/views/editProduct.html',
          controller: 'IndexEditProductController',
          size: 'sm',
          resolve: {
            price: function () {
              return product.price;
            }
          }
        });
        editProductModal.result.then(function (productEditModel) {
          StoreService.editStoreProduct(product.id, productEditModel).then(
            function (response) {
              $scope.products[index].price = Number(response.data.price);
              ngToast.success({
                content: "Price updated",
                dismissButton: true
              });
            },
            function (response) {
              ngToast.danger({
                content: "Error while updating price",
                dismissButton: true
              });
            }
          );
        });
      } else {
        ngToast.danger({
          content: "Error while updating price",
          dismissButton: true
        });
      }
    };

    function getZipcodeProducts() {
      StoreService.getZipcodeProducts({'lat': lat, 'lng': lng, 'radius': radius}).then(
        function (response) {
          $scope.products = response.data;
          for (var i = 0; i < $scope.products.length; i++) {
            $scope.products[i].price = Number($scope.products[i].price)
          }
          $scope.displayedProducts = [].concat($scope.products);
        },
        function (response) {
          ngToast.danger({
            content: "Error while loading products",
            dismissButton: true
          });
        }
      );
    }
    getZipcodeProducts();
  }

  IndexSingleStoreController.$inject = ['$scope', '$window', '$stateParams', '$uibModal', 'StoreService', 'ngToast'];

  function IndexSingleStoreController ($scope, $window, $stateParams, $uibModal, StoreService, ngToast) {

    var zipcode = $window.localStorage.zipcode;
    var lat = $window.localStorage.lat;
    var lng = $window.localStorage.lng;

    $scope.editProduct = function (product) {
      var index = $scope.products.indexOf(product);
      if (index !== -1) {
        var editProductModal = $uibModal.open({
          animation: true,
          templateUrl: '/static/js/modals/views/editProduct.html',
          controller: 'IndexEditProductController',
          size: 'sm',
          resolve: {
            price: function () {
              return product.price;
            }
          }
        });
        editProductModal.result.then(function (productEditModel) {
          StoreService.editStoreProduct(product.id, productEditModel).then(
            function (response) {
              $scope.products[index].price = Number(response.data.price);
              ngToast.success({
                content: "Price updated",
                dismissButton: true
              });
            },
            function (response) {
              ngToast.danger({
                content: "Error while updating price",
                dismissButton: true
              });
            }
          );
        });
      } else {
        ngToast.danger({
          content: "Error while updating price",
          dismissButton: true
        });
      }
    };

    function getStore() {
      StoreService.getStore($stateParams.storeId).then(
        function (response) {
          $scope.store = response.data;
          StoreService.getStoreProducts($stateParams.storeId).then(
            function (response) {
              $scope.products = response.data;
              for (var i = 0; i < $scope.products.length; i++) {
                $scope.products[i].price = Number($scope.products[i].price)
              }
              $scope.displayedProducts = [].concat($scope.products);
            },
            function (response) {
              ngToast.danger({
                content: "Error while loading products",
                dismissButton: true
              });
            }
          );
        },
        function (response) {
          ngToast.danger({
            content: "Error while loading store",
            dismissButton: true
          });
        }
      );
    }
    getStore();
  }

  IndexCartController.$inject = ['$scope', '$window', 'ngToast', 'ngCart', 'NgMap'];

  function IndexCartController ($scope, $window, ngToast, ngCart, NgMap) {

    var zipcode = $window.localStorage.zipcode;
    $scope.lat = $window.localStorage.lat;
    $scope.lng = $window.localStorage.lng;

    $scope.routePath = function () {
      $scope.wayPoints = [];
      var seenStores = [];
      var products = ngCart.getItems();
      for (var i = 0; i < products.length; i++) {
        var wayPoint = {
          location: {
            lat: products[i].getData().address.lat,
            lng: products[i].getData().address.lng
          },
          stopover: true
        };
        var index = seenStores.indexOf(products[i].getData().id);
        if (index == -1) {
          seenStores.push(products[i].getData().id);
          $scope.wayPoints.push(wayPoint);
        }
      }
    };
  }

  IndexEditProductController.$inject = ['$scope', '$uibModalInstance', 'price'];

  function IndexEditProductController ($scope, $uibModalInstance, price) {

    $scope.productEditModel = {
      'price': price
    };
    $scope.productEditFields = [
      {
        key: 'price',
        type: 'input',
        templateOptions: {
          type: 'number',
          placeholder: 'Price',
          required: true
        }
      }
    ];

    $scope.editProduct = function () {
      $uibModalInstance.close($scope.productEditModel);
    };

    $scope.cancel = function () {
      $uibModalInstance.dismiss('cancel');
    };
  }

})();
