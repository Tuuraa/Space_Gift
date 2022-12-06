import Payment


async def get_banks():
    payment_types: dict = await Payment.client_payment_types()
    payment_types_list = []

    for i in payment_types.keys():
        payment_types_list.append(i)

    return payment_types_list


async def create_order(payment_type, rub_sum):
    order: dict = await Payment.create_order(payment_type, rub_sum)
    print(order)
    number = order.get("payment_requisites")
    amount = order.get("final_rub_sum")
    order_id = order.get("order_id")

    return number, amount, order_id


async def check_order(ids):
    order: dict = await Payment.get_order(ids)
    print(order)