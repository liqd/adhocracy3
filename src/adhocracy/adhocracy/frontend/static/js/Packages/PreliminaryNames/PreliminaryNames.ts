class PreliminaryNames {
    private state : number;

    constructor() {
        this.state = 0;
    }

    public nextPreliminary() : string {
        this.state += 1;
        return "@pn" + this.state.toString();
    }

    public isPreliminary(path : string) : boolean {
        return path[0] === "@";
    }
}

export = PreliminaryNames;
