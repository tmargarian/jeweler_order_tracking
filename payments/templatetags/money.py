from django import template
register = template.Library()


@register.filter()
def format_price(price_cents):
    return f'{int(price_cents) / 100:.0f}'
