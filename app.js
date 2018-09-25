(function(){
'use strict';

angular.module("dmathAPP",[])
.controller('propositionLogic',propositionLogic)
.service('requestService', requestService)
.constant('baseURL','http://188.131.137.105:8085/');

propositionLogic.$inject = ['requestService']
function propositionLogic(requestService){
	var pl = this;

	pl.formulaStr = "";

	pl.submit = function(){
		var promise = requestService.getTF(pl.formulaStr);
		promise.then(function(response){
			pl.errorMsg = "";
			pl.TF = response.data;
			pl.heads = [];
			pl.row = [];
			for(var colName in pl.TF){
				if(colName!=="output")
					pl.heads.push(colName);
			}
			pl.heads.push('output');
			for(var idx in pl.TF.output){
				var dct = {};
				for(var colName in pl.TF) {
					dct[colName] = pl.TF[colName][idx];
				}
				pl.row.push(dct);
			}
			// console.log(pl.heads);
			// console.log(pl.row);
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
			url: baseURL,
			params: {
				"formula": formulaStr
			}
		});
		return response;
	};
}

})();

