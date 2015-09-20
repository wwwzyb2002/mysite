/*
main.js
 */

require(['/static/test/server.js'], function (server) {
    console.log("main.js")
    server.initSearch();
    server.loadEnvInfos();
    server.loadPDInfos();
    server.loadServers();
})