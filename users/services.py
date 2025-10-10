import stripe
from django.conf import settings
from forex_python.converter import CurrencyRates

stripe.api_key = settings.STRIPE_SECRET_KEY


def convert_usd_to_rub(amount_usd):
    # c = CurrencyRates()
    # rate = c.get_rate("USD", "RUB")
    # amount_rub = amount_usd * rate
    # return int(amount_rub * 100)
    fixed_rate = 95  # курс 95 рублей за доллар
    return int(amount_usd * fixed_rate * 100)


def create_stripe_product(name, description=None):
    return stripe.Product.create(name=name, description=description)


def create_stripe_price(product_id, unit_amount, currency="rub"):
    return stripe.Price.create(
        product=product_id, unit_amount=unit_amount, currency=currency
    )


def create_checkout_session(price_id, success_url, cancel_url):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
