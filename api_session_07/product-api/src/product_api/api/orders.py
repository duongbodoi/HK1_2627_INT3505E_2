from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Order, OrderItem, Product
from ..errors import NotFound, OutOfStock
from ..schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def _get_active_product(pid):
    p = db.session.get(Product, pid)
    if p is None or p.archived:
        raise NotFound(f"product {pid} not found")
    return p


@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.get_json())

    # Gộp các dòng trùng product_id: [{p1,2},{p1,3}] -> {p1: 5}
    wanted = {}
    for it in body["items"]:
        pid = it["product_id"]
        wanted[pid] = wanted.get(pid, 0) + it["quantity"]

    order = Order()
    try:
        for pid in sorted(wanted):          # sắp xếp để tránh deadlock khi nhiều đơn cùng lúc
            qty = wanted[pid]
            product = _get_active_product(pid)

            # Trừ kho nguyên tử, giống endpoint reserve
            result = db.session.execute(
                db.update(Product)
                .where(Product.id == pid, Product.qty_in_stock >= qty)
                .values(qty_in_stock=Product.qty_in_stock - qty)
            )
            if result.rowcount == 0:
                raise OutOfStock(f"not enough stock for product {pid}")

            order.items.append(OrderItem(
                product_id=pid,
                quantity=qty,
                unit_price_cents=product.price_cents,
            ))

        db.session.add(order)
        db.session.commit()                 # commit MỘT LẦN cho cả đơn
    except Exception:
        db.session.rollback()               # lỗi ở bất kỳ dòng nào thì hoàn trả hết
        raise

    return OrderOut().dump(order), 201


@orders_bp.get("")
def list_orders():
    page = max(1, request.args.get("page", 1, type=int))
    size = min(100, max(1, request.args.get("size", 20, type=int)))

    rows = db.session.execute(
        db.select(Order)
        .options(selectinload(Order.items))     # chống N+1: 2 query thay vì 1+N
        .order_by(Order.id)
        .offset((page - 1) * size).limit(size)
    ).scalars().all()
    total = db.session.scalar(db.select(func.count()).select_from(Order))

    return jsonify(items=OrderOut(many=True).dump(rows),
                   page=page, size=size, total=total), 200


@orders_bp.get("/<int:id>")
def get_order(id):
    order = db.session.execute(
        db.select(Order).options(selectinload(Order.items)).where(Order.id == id)
    ).scalar_one_or_none()
    if order is None:
        raise NotFound(f"order {id} not found")
    return OrderOut().dump(order), 200