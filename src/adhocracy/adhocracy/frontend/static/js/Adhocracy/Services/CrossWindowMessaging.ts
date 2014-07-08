export interface IMessage {

    data: {};
    name: string;
    sender: number;

}


export class Service {

    private uid : number;

    constructor(public _postMessage) {

        var _self = this;
        _self.uid = 0;

    }

    private postMessage(name: string, data: {}) : void {

        var _self = this;

        var message : IMessage = {
            data: data,
            name: name,
            sender: _self.uid
        };

        _self._postMessage(JSON.stringify(message));
    }

    postResize(height: number) : void {

        var _self = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }

}
