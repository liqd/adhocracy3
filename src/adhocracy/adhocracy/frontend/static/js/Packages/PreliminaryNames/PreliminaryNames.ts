class PreliminaryNames {
    state : number;

    constructor() {
        this.state = 0;
    }

    public next() : string {
        this.state += 1;
        return "pn" + this.state.toString();
    }
}

export = PreliminaryNames;
