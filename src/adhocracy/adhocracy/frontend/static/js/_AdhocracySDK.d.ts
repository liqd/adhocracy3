declare module AdhocracySDK {
    export interface IAdhocracy {
        noConflict : () => IAdhocracy;
        init : (o : string, callback) => void;
        embed : (selector : string) => void;
        postMessage : (win : Window, name : string, data : {}) => void;
    }
}

declare var adhocracy : AdhocracySDK.IAdhocracy;
