class OrderError(Exception):
    """주문 처리 과정에서 발생하는 기본 예외입니다."""


class InvalidOrderIdError(OrderError):
    """주문번호 형식이 올바르지 않을 때 발생합니다."""


class OrderNotFoundError(OrderError):
    """주문번호에 해당하는 주문이 없을 때 발생합니다."""


def validate_order_id(value: str) -> int:
    """
    사용자에게 입력받은 주문번호를 검증합니다.

    Args:
        value: 사용자가 입력한 문자열

    Returns:
        검증된 정수형 주문번호

    Raises:
        InvalidOrderIdError: 빈 값, 숫자가 아닌 값,
        0 이하의 숫자가 입력된 경우
    """
    value = value.strip()

    if not value:
        raise InvalidOrderIdError("주문번호를 입력해야 합니다.")

    try:
        order_id = int(value)
    except ValueError as error:
        raise InvalidOrderIdError(
            "주문번호는 숫자로 입력해야 합니다."
        ) from error

    if order_id <= 0:
        raise InvalidOrderIdError(
            "주문번호는 1 이상의 숫자여야 합니다."
        )

    return order_id


def find_order(orders: list[dict], order_id: int) -> dict:
    """
    주문 목록에서 주문번호에 해당하는 주문을 조회합니다.

    Args:
        orders: 주문 목록
        order_id: 조회할 주문번호

    Returns:
        조회된 주문 정보

    Raises:
        OrderNotFoundError: 주문번호에 해당하는 주문이 없는 경우
    """
    for order in orders:
        if order.get("id") == order_id:
            return order

    raise OrderNotFoundError(
        f"주문번호 {order_id}에 해당하는 주문을 찾을 수 없습니다."
    )


def remove_order(orders: list[dict], order_id: int) -> dict:
    """
    주문 목록에서 주문번호에 해당하는 주문을 삭제합니다.

    Args:
        orders: 주문 목록
        order_id: 삭제할 주문번호

    Returns:
        삭제된 주문 정보

    Raises:
        OrderNotFoundError: 주문번호에 해당하는 주문이 없는 경우
    """
    order = find_order(orders, order_id)
    orders.remove(order)

    return order