# app_codefirst.py
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate
app = Flask(__name__)
app.config.update(
    API_TITLE="Product API (Code-First)",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/",
    OPENAPI_SWAGGER_UI_PATH="/docs",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)
api = Api(app)



class ProductInSchema(Schema):          # input khi POST
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))


class ProductSchema(Schema):            # output trả về
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()


PRODUCTS = {
    1: {"id": 1, "sku": "SKU-001", "name": "Bàn phím", "price_cents": 500000, "cost_cents": 300000},
}

blp = Blueprint("products", __name__, url_prefix="/api/v1/products",
                description="Quản lý sản phẩm")



@blp.route("/")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """Danh sách sản phẩm"""                      # docstring → summary trong spec
        return list(PRODUCTS.values())

    @blp.arguments(ProductInSchema)                     # validate body, sai → 422
    @blp.response(201, ProductSchema)                   # lọc output qua schema
    @blp.alt_response(409, description="SKU đã tồn tại")
    def post(self, data):
        """Tạo sản phẩm"""
        if any(p["sku"] == data["sku"] for p in PRODUCTS.values()):
            abort(409, message="SKU đã tồn tại")
        new_id = max(PRODUCTS, default=0) + 1
        PRODUCTS[new_id] = {"id": new_id, **data}
        return PRODUCTS[new_id]


@blp.route("/<int:id>")
class ProductItem(MethodView):
    @blp.response(200, ProductSchema)
    @blp.alt_response(404, description="Không tìm thấy")
    def get(self, id):
        """Lấy một sản phẩm"""
        if id not in PRODUCTS:
            abort(404, message="Không tìm thấy sản phẩm")
        return PRODUCTS[id]


api.register_blueprint(blp)     

if __name__ == "__main__":
    app.run(port=5000, debug=True)