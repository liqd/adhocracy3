export class Service {
    private state : number;

    constructor() {
        this.state = 0;
    }

    public nextPreliminary() : string {
        this.state += 1;
        return "@pn" + this.state.toString();
    }

    public isPreliminary(path : string) : boolean {
        return path.length > 2 && path[0] === "@" && path[1] !== "@";
    }
}
