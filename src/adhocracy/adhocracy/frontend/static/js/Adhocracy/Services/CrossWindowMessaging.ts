export interface IMessage {
    data: {};
    name: string;
    sender: string;
}

export class Service {

    private uid : number;

    constructor(public _postMessage) {
        var _self : Service = this;

    }

    private postMessage(name: string, data: {}) : void {
        var _self : Service = this;

        var message : IMessage = {
            data: data,
            name: name,
            sender: _self.uid
        };

        _self._postMessage(JSON.stringify(message), "*");
    }

    postResize(height: number) : void {
        var _self : Service = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }
}


export var factory = ($window) => {
    var postMessageToParent = (data, origin) => $window.parent.postMessage(data, origin);
    return new Service(postMessageToParent, $window);
};
