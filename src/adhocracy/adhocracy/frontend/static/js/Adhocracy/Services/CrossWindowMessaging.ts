export interface IMessage {
    data : IMessageData;
    name : string;
}


export interface IMessageData {}


export class Service {

    private embedderOrigin : string = "*";

    constructor(public _postMessage, public $window, public $interval) {
        var _self = this;

        _self.manageResize();
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

    public postResize(height: number) : void {
        var _self : Service = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }

    /**
     * Body does not trigger resize events. So we have to guess when its height
     * has changed ourselves.
     */
    private manageResize() : void {
        var _self = this;

        var postResizeIfChange = (() => {
            var oldHeight = 0;
            return () => {
                var height = _self.$window.document.body.clientHeight;
                if (height !== oldHeight) {
                    oldHeight = height;
                    _self.postResize(height);
                }
            };
        })();

        // Check for changes regulary
        _self.$interval(postResizeIfChange, 100);
    }
}


export var factory = ($window, $interval) => {
    var postMessageToParent = (data, origin) => $window.parent.postMessage(data, origin);
    return new Service(postMessageToParent, $window, $interval);
};
