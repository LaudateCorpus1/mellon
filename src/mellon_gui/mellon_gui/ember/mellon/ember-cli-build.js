/*jshint node:true*/
/* global require, module */
var EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
  var app = new EmberApp(defaults, {
    // Add options here
  });

  // Use `app.import` to add additional libraries to the generated
  // output files.
  //
  // If you need to use different assets in different
  // environments, specify an object as the first parameter. That
  // object's keys should be the environment name and the values
  // should be the asset to use in that environment.
  //
  // If the library that you are including contains AMD or ES6
  // modules that you would like to import into your application
  // please specify an object with the list of modules as keys
  // along with the exports of each module as its value.
  
  <!-- Core CSS - Include with every page -->
  <!-- SB Admin CSS - Include with every page -->
  //app.import('bower_components/bootstrap/dist/css/bootstrap-theme.css');
  app.import('vendor/sb-admin-v2/css/bootstrap.min.css');
  <!-- Page-Level Plugin CSS - Tables -->
  app.import('vendor/sb-admin-v2/css/plugins/dataTables/dataTables.bootstrap.css');
  <!-- SB Admin CSS - Include with every page -->
  app.import('vendor/sb-admin-v2/css/sb-admin.css');
  
  

  <!-- Core Scripts - Include with every page -->
  app.import('bower_components/bootstrap/dist/js/bootstrap.js');
  //app.import('vendor/sb-admin-v2/js/plugins/metisMenu/jquery.metisMenu.js');

  <!-- Page-Level Plugin Scripts - Tables -->
  app.import('vendor/sb-admin-v2/js/plugins/dataTables/jquery.dataTables.js');
  app.import('vendor/sb-admin-v2/js/plugins/dataTables/dataTables.bootstrap.js');

  <!-- SB Admin Scripts - Include with every page -->
  app.import('vendor/sb-admin-v2/js/sb-admin.js');
  
  <!-- Page-Level Plugin Scripts - Dashboard -->
  //app.import('bower_components/raphael/raphael.min.js');
  //app.import('bower_components/morris.js/morris.js');

  <!-- Page-Level Demo Scripts - Dashboard - Use for reference -->
  //app.import('vendor/sb-admin-v2/js/demo/dashboard-demo.js');

  return app.toTree();
};
