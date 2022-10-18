# API Routes

<link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.0/swagger-ui.css" />
<style>
  .topbar {
    display: none !important;
  }
  .info {
    display: none !important;
  }
  .scheme-container {
    display: none !important;
  }
  .response-col_description__inner {
    margin-top: -15px;
  }
  .response-col_links {
    display: none;
  }
</style>

<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@3.52.0/swagger-ui-bundle.js" charset="UTF-8"></script>
<script src="https://unpkg.com/swagger-ui-dist@3.52.0/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
<script>
window.onload = function() {
  // Begin Swagger UI call region
  const ui = SwaggerUIBundle({
    url: "../api-spec.yaml",
    dom_id: '#swagger-ui',
    deepLinking: false,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    layout: "StandaloneLayout",
    supportedSubmitMethods: [],
    validatorUrl: null,
  });
  // End Swagger UI call region
  window.ui = ui;
};
</script>
