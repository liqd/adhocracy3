import * as AdhEuthCollaberativeTexteditingModule from "./CollaborativeTextediting/Module";

export var moduleName = "adhEuth";

export var register = (angular) => {
	AdhEuthCollaberativeTexteditingModule.register(angular);

	angular
        .module(moduleName, [
	           AdhEuthCollaberativeTexteditingModule.moduleName
	   ]);
};
