import * as AdhEuthCollaberativeTexteditingModule from "./CollaborativeTextediting/Module";
import * as AdhEuthIdeaCollectionModule from "./IdeaCollection/Module";

export var moduleName = "adhEuth";

export var register = (angular) => {
	AdhEuthCollaberativeTexteditingModule.register(angular);
	AdhEuthIdeaCollectionModule.register(angular);

	angular
        .module(moduleName, [
	        AdhEuthCollaberativeTexteditingModule.moduleName,
			AdhEuthIdeaCollectionModule.moduleName
		]);
};
