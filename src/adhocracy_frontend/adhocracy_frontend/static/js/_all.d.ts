/* tslint:disable */
/// <reference path="../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

declare module "angularAnimate" {}
declare module "angularAria" {}
declare module "angularMessages" {}
declare module "angularCache" {}
declare module "angularTranslate" {}
declare module "angularTranslateLoader" {}
declare module "angularElastic" {}
declare module "angularScroll" {}
declare module "angularFlow" {}

declare module "sticky" {
    export var Sticky : any;
}

declare module "modernizr" {
    export var Modernizr : ModernizrStatic;
}

/**
 * Fake module description for Kris Kowal's q
 *
 * This is actually the description of angular.IQService.
 *
 * We use q as a drop-in replacement in testing as it is compatible with both
 * node.js and browsers and does not require angular.
 *
 * While both modules are very much compatible[0], the descriptions from
 * DefinitelyTyped are not.  So we use this one instead.
 *
 * I did not find a simple way of saying "this module has just the same API as
 * angular.IQService" because one is a module and the other is an interface. So I
 * copied the whole description over.
 *
 * [0]: https://docs.angularjs.org/api/ng/service/$q#differences-between-kris-kowal-s-q-and-q
 */
declare module "q" {
    export function all(promises: angular.IPromise<any>[]): angular.IPromise<any[]>;
    export function all(promises: { [id: string]: angular.IPromise<any>; }): angular.IPromise<{ [id: string]: any }>;
    export function defer<T>(): angular.IDeferred<T>;
    export function reject(reason?: any): angular.IPromise<void>;
    export function when<T>(value: angular.IPromise<T>): angular.IPromise<T>;
    export function when<T>(value: T): angular.IPromise<T>;
    export function when(): angular.IPromise<void>;
}

/**
 * Flow, ng-flow do not have DefinitelyTyped interfaces.  This is a
 * preliminary attempt to fix that.
 *
 * FIXME: get into DefinitelyTyped, of course.
 */
declare class Flow {
    events : any;
    files : FlowFile[];
    opts : FlowOpts;
    preventEvent : (event : any) => any;
    support : boolean;
    supportDirectory : boolean;
    upload : () => any;
    resume : () => any;
    pause : () => any;
    cancel : () => any;
    on : (event : string, callback : Function) => void;
}

declare class FlowFile {
    file : {
        FilelastModifiedDate : Date;
        name : string;
        size : number;
        type : string;
        webkitRelativePath : string;
        mozSlice? : any;
        webkitSlice? : any;
    };
    chunks : FlowChunk[];
}

declare class FlowChunk {
}

declare class FlowOpts {
    chunkRetryInterval : number;
    chunkSize : number;
    fileParameterName : string;
    forceChunkSize : boolean;
    generateUniqueIdentifier : any;
    headers : any;
    maxChunkRetries : number;
    method : string;
    onDropStopPropagation : boolean;
    permanentErrors : number[];
    preprocess : any;
    prioritizeFirstAndLastChunk : boolean;
    progressCallbacksInterval : number;
    query : any;
    simultaneousUploads : number;
    singleFile : boolean;
    speedSmoothingFactor : number;
    target : string;
    testChunks : boolean;
    withCredentials : boolean;

    // these are not native to flow but used by custom functions
    minimumWidth : number;
    maximumByteSize : number;
    acceptedFileTypes : string[];
}

declare module "markdownit" {}
declare module "socialSharePrivacy" {}
declare module "adhTemplates" {}
declare module "polyfiller" {
    export function polyfill(options : string) : void;
    export function setOptions(options : any) : void;
    export function setOptions(options1 : any, options2 : any) : void;
}