from flask import Flask, jsonify, render_template_string
import yaml

app = Flask(__name__)

# Đọc file tasks_api.yaml
def load_spec():
    with open('tasks_api.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.route('/openapi.json')
def spec_json():
    """Trả về spec dưới định dạng JSON cho Swagger UI đọc"""
    spec = load_spec()
    return jsonify(spec)

@app.route('/docs')
def docs():
    """Render giao diện Swagger UI qua CDN"""
    SWAGGER_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Tasks API - Swagger UI</title>
      <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui-bundle.js"></script>
      <script>
        window.onload = function() {
          window.ui = SwaggerUIBundle({
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout"
          });
        }
      </script>
    </body>
    </html>
    """
    return render_template_string(SWAGGER_HTML)

if __name__ == '__main__':
    app.run(debug=True)