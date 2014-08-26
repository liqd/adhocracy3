class PreliminaryNames {
    private state : number;

    constructor() {
        this.state = 0;
    }

    public next() : string {
        this.state += 1;
        return "pn" + this.state.toString();
    }

    public nextPreliminary() : string {
        return "@" + this.next();
    }

    public isPreliminary(path : string) : boolean {
        return path[0] === "@";
    }
}

export = PreliminaryNames;
