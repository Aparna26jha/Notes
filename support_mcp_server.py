from fastmcp import FastMCP

mcp = FastMCP("Order Support MCP Server")

# -------------------------------------------------------------------
# Mock database
# -------------------------------------------------------------------
ORDER_DB = {
    "ORD123": {
        "status": "Shipped",
        "item": "Wireless Headphones",
        "expected_delivery": "Tomorrow"
    },
    "ORD456": {
        "status": "Processing",
        "item": "Mechanical Keyboard",
        "expected_delivery": "Next Tuesday"
    },
    "ORD789": {
        "status": "Delivered",
        "item": "Gaming Mouse",
        "expected_delivery": "Delivered Yesterday"
    },
    "ORD321": {
        "status": "Out for Delivery",
        "item": "Laptop Stand",
        "expected_delivery": "Today"
    },
    "ORD654": {
        "status": "Cancelled",
        "item": "Smart Watch",
        "expected_delivery": "N/A"
    },
    "ORD999": {
        "status": "Delayed",
        "item": "Bluetooth Speaker",
        "expected_delivery": "In 3 days"
    },
    "ORD777": {
        "status": "Processing",
        "item": "USB Hub",
        "expected_delivery": "Next Monday"
    },
    "ORD888": {
        "status": "Shipped",
        "item": "Laptop Bag",
        "expected_delivery": "Tomorrow"
    }
}


# -------------------------------------------------------------------
# MCP Tools
# -------------------------------------------------------------------
@mcp.tool()
def check_order_status(order_id: str) -> str:
    """
    Check the shipping status and expected delivery of a customer's order.
    Requires an order ID like ORD123.
    """
    order_id = order_id.upper().strip()
    order = ORDER_DB.get(order_id)

    if not order:
        return f"I could not find order {order_id} in the system. Please verify the number."

    return (
        f"Order {order_id}: {order['item']} is currently '{order['status']}'. "
        f"Expected delivery: {order['expected_delivery']}."
    )


@mcp.tool()
def calculate_refund_eligibility(days_since_purchase: int) -> str:
    """
    Determine if a customer is eligible for a refund based on how many days ago they purchased the item.
    """
    if days_since_purchase <= 30:
        return "Eligible for a full refund."
    elif days_since_purchase <= 60:
        return "Eligible for store credit only."
    else:
        return "Not eligible for a refund. The 60-day return window has expired."


if __name__ == "__main__":
    # stdio transport is ideal for local MCP client connection
    mcp.run()
