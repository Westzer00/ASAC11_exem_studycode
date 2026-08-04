# 주문 목록
orders = [
    {
        "id": 1,
        "customer": "홍길동",
        "menu": "아메리카노",
        "quantity": 2,
        "price": 4500,
        "status": "주문 완료"
    },
    {
        "id": 2,
        "customer": "김철수",
        "menu": "카페라떼",
        "quantity": 1,
        "price": 5000,
        "status": "주문 대기"
    },
    {
        "id": 3,
        "customer": "이영희",
        "menu": "카푸치노",
        "quantity": 1,
        "price": 5500,
        "status": "주문 완료"
    },
    {
        "id": 4,
        "customer": "박민수",
        "menu": "바닐라라떼",
        "quantity": 2,
        "price": 5800,
        "status": "배송 중"
    },
    {
        "id": 5,
        "customer": "최유리",
        "menu": "치즈케이크",
        "quantity": 1,
        "price": 6500,
        "status": "배송 완료"
    }
]

def search_order(order_id):
    for order in orders:
        if order["id"] == order_id:
            return order
    return None


order_id = int(input("조회할 주문 번호를 입력하세요: "))

result = search_order(order_id)

if result:
    print("\n주문 조회 결과")
    print(f"주문번호 : {result['id']}")
    print(f"고객명   : {result['customer']}")
    print(f"메뉴     : {result['menu']}")
    print(f"수량     : {result['quantity']}")
    print(f"가격     : {result['price']}원")
    print(f"상태     : {result['status']}")
else:
    print("해당 주문을 찾을 수 없습니다.")