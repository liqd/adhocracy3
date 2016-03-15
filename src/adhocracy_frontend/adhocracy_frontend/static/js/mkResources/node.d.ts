declare module "http" {
    function request(config : any, callback : Function) : any;
}

declare module "fs" {
    function readFile(fileName : string, encoding : string, callback : (err : any, data : string) => void) : void;
    function writeFileSync(fileName : string, content : string) : void;
}

declare module "node-fs" {
    function mkdirSync(path : string, mode : number, somearg : boolean) : void;
}
