from flask import Flask, jsonify, render_template_string, request
import yaml

app = Flask(__name__)
app.json.ensure_ascii = False  # Giữ nguyên tiếng Việt trong JSON trả về

# Đọc file tasks_api.yaml
def load_spec():
    with open('tasks_api.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.route('/openapi.json')
def spec_json():
    """Trả về spec dưới định dạng JSON cho Swagger UI đọc"""
    spec = load_spec()
    # Trỏ server về chính host đang chạy (http) để "Try it out" gọi được API
    spec['servers'] = [{'url': request.host_url + 'v1', 'description': 'Máy chủ'}]
    return jsonify(spec)


# ===================== Tasks API (theo tasks_api.yaml) =====================

# Lưu task trong bộ nhớ (mất khi tắt server) - thay cho cơ sở dữ liệu
TASKS = {}
next_id = 1

STATUS_ENUM = ['inProgress', 'done', 'overdue']
PRIORITY_ENUM = ['high', 'nomal', 'low']
FIELDS = ['title', 'status', 'priority', 'dueDate', 'assigneeId']


def problem(status, title, detail):
    """Tạo response lỗi theo chuẩn Problem Details (RFC 7807)"""
    body = {
        'type': 'about:blank',
        'title': title,
        'status': status,
        'detail': detail,
        'instance': request.path,
    }
    return jsonify(body), status


def validate_task_input(data):
    """Kiểm tra body theo schema taskInput, trả về thông báo lỗi hoặc None"""
    if not isinstance(data, dict):
        return 'Body phải là một JSON object.'
    if 'title' in data and not isinstance(data['title'], str):
        return "Trường 'title' phải là chuỗi."
    if 'status' in data and data['status'] not in STATUS_ENUM:
        return f"Trường 'status' phải là một trong {STATUS_ENUM}."
    if 'priority' in data and data['priority'] not in PRIORITY_ENUM:
        return f"Trường 'priority' phải là một trong {PRIORITY_ENUM}."
    if 'dueDate' in data and not isinstance(data['dueDate'], str):
        return "Trường 'dueDate' phải là chuỗi."
    if 'assigneeId' in data and (not isinstance(data['assigneeId'], int)
                                 or isinstance(data['assigneeId'], bool)):
        return "Trường 'assigneeId' phải là số nguyên."
    return None


def task_not_found(task_id):
    return problem(404, 'Not Found', f'Không tìm thấy task có id = {task_id}.')


@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    """Danh sách task, có hỗ trợ filter theo status (mặc định inProgress)"""
    status = request.args.get('status', 'inProgress')
    if status not in STATUS_ENUM:
        return problem(400, 'Bad Request', f"Tham số 'status' phải là một trong {STATUS_ENUM}.")
    return jsonify([t for t in TASKS.values() if t.get('status') == status])


@app.route('/v1/tasks', methods=['POST'])
def create_task():
    """Tạo mới 1 task"""
    global next_id
    data = request.get_json(silent=True)
    error = validate_task_input(data)
    if error:
        return problem(400, 'Bad Request', error)
    if not data.get('title'):
        return problem(400, 'Bad Request', "Trường 'title' là bắt buộc khi tạo task.")

    task = {'id': next_id, 'status': 'inProgress'}
    task.update({k: data[k] for k in FIELDS if k in data})
    TASKS[next_id] = task
    next_id += 1
    return jsonify(task), 201


@app.route('/v1/tasks/<int:task_id>', methods=['GET'])
def get_task_by_id(task_id):
    """Xem task theo id"""
    if task_id not in TASKS:
        return task_not_found(task_id)
    return jsonify(TASKS[task_id])


@app.route('/v1/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    """Edit task - chỉ cập nhật các trường được gửi lên"""
    if task_id not in TASKS:
        return task_not_found(task_id)
    data = request.get_json(silent=True)
    error = validate_task_input(data)
    if error:
        return problem(400, 'Bad Request', error)

    TASKS[task_id].update({k: data[k] for k in FIELDS if k in data})
    return jsonify(TASKS[task_id])


@app.route('/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Xoá task"""
    if task_id not in TASKS:
        return task_not_found(task_id)
    del TASKS[task_id]
    return '', 204

# ===========================================================================

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