(function(){
'use strict';

angular.module("dmathAPP",[])
.controller('propositionLogic',propositionLogic)
.service('requestService', requestService)
.constant('baseURL','188.131.137.105:8085');

propositionLogic.$inject = ['requestService']
function propositionLogic(requestService){
	var pl = this;

	pl.formulaStr = "";

	pl.submit = function(){
		var promise = requestService.getTF(pl.formulaStr);
		promise.then(function(response){
			pl.errorMsg = "";
			pl.TF = Json.parse(response.data);
			console.log(pl.TF);
		}).catch(function(error){
			pl.errorMsg = error;
			console.log(error);
		});
	};

	
}

requestService.$inject = ['$http','baseURL']
function requestService($http,baseURL){
	var service = this;

	service.getTF = function(formulaStr) {
		var response = $http({
			method: "GET",
			url: (baseURL + '/formula=' + formulaStr)
		});
		return response;
	};
}

})();