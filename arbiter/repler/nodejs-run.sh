#!/bin/bash

cat >main.js <<EOF
var riffle = require('jsriffle');

riffle.SetFabric(process.env.WS_URL);
$EXIS_SETUP

var app = riffle.Domain(process.env.DOMAIN);
var backend = app.Subdomain("example");
var client = app.Subdomain("example");

backend.onJoin = function() {
    $EXIS_REPL_CODE
    console.log("___SETUPCOMPLETE___");
};

backend.Join()
EOF

echo "___BUILDCOMPLETE___"

which nodejs
if [ $? -ne 0 ]; then
    node main.js
else
    nodejs main.js
fi