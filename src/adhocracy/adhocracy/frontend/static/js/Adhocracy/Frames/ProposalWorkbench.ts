/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>

declare var $ : any;  // FIXME

var obvieltemplate = require('obvieltemplate');
var obviel = require('obviel');

import Obviel = require('Adhocracy/Obviel');
import Util = require('Adhocracy/Util');

export function open_proposals(uri, done) {

    Obviel.register_transformer();  // FIXME: this should not happen here.

/*
    var proposal_dags_with_cheating = [{
        ifaces: ['IName'],
        meta: { path: '...' },
        data: { 'adhocracy#interfaces#IName': { name: 'proposal DAG 1' } },
    }, {
        ifaces: ['IName'],
        meta: { path: '...' },
        data: { 'adhocracy#interfaces#IName': { name: 'proposal DAG 1' } },
    }];
*/

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IPool',
        name: 'ProposalWorkbench',
        obvtUrl: 'templates/ProposalWorkbench.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IPool',
        name: 'Directory',
        obvtUrl: 'templates/Directory.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IName',
        name: 'DirectoryEntry',
        obvtUrl: 'templates/DirectoryEntry.obvt',
    });

    $('#adhocracy').render('/adhocracy/', 'ProposalWorkbench').done(done);
}
