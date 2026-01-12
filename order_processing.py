BASE_CURRENCY = "USD"
SALES_TAX_RATE = 0.21

COUPON_CODE_SAVE10 = "SAVE10"
COUPON_CODE_SAVE20 = "SAVE20"
COUPON_CODE_VIP = "VIP"

DISCOUNT_RATE_SAVE10 = 0.10
DISCOUNT_RATE_SAVE20 = 0.20
MINIMUM_SUBTOTAL_FOR_SAVE20 = 200
ALTERNATIVE_DISCOUNT_RATE_SAVE20 = 0.05

VIP_DISCOUNT_REGULAR = 50
VIP_DISCOUNT_SMALL_ORDER = 10
VIP_SMALL_ORDER_LIMIT = 100

ORDER_ID_SUFFIX = "X"


def extract_checkout_data(request):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon_code = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon_code, currency


def validate_required_fields(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        return BASE_CURRENCY
    return currency


def validate_order_items(items):
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items):
    subtotal_amount = 0
    for item in items:
        subtotal_amount = subtotal_amount + item["price"] * item["qty"]
    return subtotal_amount


def calculate_discount_amount(subtotal, coupon_code):
    if coupon_code is None or coupon_code == "":
        return 0

    if coupon_code == COUPON_CODE_SAVE10:
        return int(subtotal * DISCOUNT_RATE_SAVE10)

    if coupon_code == COUPON_CODE_SAVE20:
        if subtotal >= MINIMUM_SUBTOTAL_FOR_SAVE20:
            return int(subtotal * DISCOUNT_RATE_SAVE20)
        return int(subtotal * ALTERNATIVE_DISCOUNT_RATE_SAVE20)

    if coupon_code == COUPON_CODE_VIP:
        if subtotal < VIP_SMALL_ORDER_LIMIT:
            return VIP_DISCOUNT_SMALL_ORDER
        return VIP_DISCOUNT_REGULAR

    raise ValueError("unknown coupon")


def calculate_amount_after_discount(subtotal, discount):
    amount_after_discount = subtotal - discount
    if amount_after_discount < 0:
        amount_after_discount = 0
    return amount_after_discount


def calculate_tax_amount(amount):
    return int(amount * SALES_TAX_RATE)


def generate_order_id(user_id, items_count):
    return str(user_id) + "-" + str(items_count) + "-" + ORDER_ID_SUFFIX


def process_checkout(request):
    user_id, items, coupon_code, currency = extract_checkout_data(request)

    currency = validate_required_fields(user_id, items, currency)
    validate_order_items(items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount_amount(subtotal, coupon_code)

    amount_after_discount = calculate_amount_after_discount(subtotal, discount)
    tax = calculate_tax_amount(amount_after_discount)
    total_amount = amount_after_discount + tax

    items_count = len(items)
    order_id = generate_order_id(user_id, items_count)

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total_amount,
        "items_count": items_count,
    }
