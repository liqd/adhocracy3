#!/bin/bash
./bin/import_resources etc/test_with_ws.ini  src/adhocracy_meinberlin/adhocracy_meinberlin/scripts/sample_bplan.json
./bin/set_workflow_state etc/test_with_ws.ini /organisation/bplan20 announce participate
