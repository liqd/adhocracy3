export interface IMessage {
    data : IMessageData;
    name : string;
}


export interface IMessageData {}


export class Service {

    private embedderOrigin : string = "*";

    constructor(public _postMessage, public $window) {
        var _self = this;

        _self.$window.addEventListener("resize", (event) => {
            var height = document.body.clientHeight;
            _self.postResize(height);
        });
    }

    public registerMessageHandler(name : string, callback : (IMessageData) => void) : void {
        var _self = this;

        _self.$window.addEventListener("message", (event) => {
            var message = JSON.parse(event.data);

            if ((event.origin === _self.embedderOrigin) && (message.name === name)) {
                callback(message.data);
            }
        });
    }

    private postMessage(name: string, data: IMessageData) : void {
        var _self : Service = this;

        var message : IMessage = {
            name: name,
            data: data
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
