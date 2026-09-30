from flask import Flask, request, jsonify

app = Flask(__name__)

# database
posts_db = [
    {"id": 1, "title": "Post 1", "content": "1231321312"},
    {"id": 2, "title": "Post 2", "content": "ádqweffasfasf"}
]

# 1. Lấy danh sách tất cả bài viết (Collection)
@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify({"posts": posts_db}), 200

# 2. Tạo một bài viết mới (Collection)
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    new_post = {
        "id": len(posts_db) + 1,
        "title": data.get("title"),
        "content": data.get("content")
    }
    posts_db.append(new_post)
    return jsonify(new_post), 201

# 3. Lấy chi tiết một bài viết (Item)
@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if post:
        return jsonify(post), 200
    return jsonify({"error": "Post not found"}), 404

# 4. Cập nhật một bài viết (Item)
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if post:
        post.update({
            "title": data.get("title", post["title"]),
            "content": data.get("content", post["content"])
        })
        return jsonify(post), 200
    return jsonify({"error": "Post not found"}), 404

# 5. Xóa một bài viết (Item)
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts_db
    posts_db = [p for p in posts_db if p["id"] != post_id]
    return '', 204

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)