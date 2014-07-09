export interface IMessage {
    data : IMessageData;
    name : string;
    sender : string;
}


export interface IMessageData {
}


export class Service {

    private uid : string;
    private embedderOrigin : string;
    private embedderID : string;

    constructor(public _postMessage, public $window) {
        var _self = this;

        _self.registerCallback("setup", function(data, sender) {
            _self.uid = data.uid;
            _self.embedderOrigin = data.embedderOrigin;
            _self.embedderID = data.embedderID;
        });
    }

    private registerCallback(name : string, callback : (IMessageData, string) => void) : void {
        var _self = this;

        _self.$window.addEventListener("message", function(event) {
            var message = JSON.parse(event.data);

            if (((name === "setup") || (event.origin === _self.embedderOrigin))
                && (message.name === name)) {
                    callback(message.data, message.sender);
                }
        });
    }

    private postMessage(name: string, data: IMessageData) : void {
        var _self : Service = this;

        var message : IMessage = {
            data: data,
            name: name,
            sender: _self.uid
        };

        _self._postMessage(JSON.stringify(message), _self.embedderOrigin);
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
