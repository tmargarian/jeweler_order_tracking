from dataclasses import dataclass
import payments.features as features
import inspect
import sys


@dataclass
class ProductMetadata(object):
    """
    Metadata for a Stripe product.
    """

    stripe_id: str
    name: str
    feature_list: list[str]
    description: str = ""
    is_default: bool = False


STANDARD = ProductMetadata(
    stripe_id="prod_P5RvlvuwVtA1We",
    name="Standard",
    description="Our only (just yet) and best product!",
    feature_list=[
        features.PRIORITY_SUPPORT,
        features.SMS_NOTIFICATIONS,
        features.PICTURE_UPLOADING,
    ],
)

# Building a Product Metadata List for usage in views.py
# this dictionary contains all plans in this file with non-empty stripe_id
product_metadata_dict = {
    member.stripe_id: member
    for name, member in inspect.getmembers(sys.modules[__name__])
    if isinstance(member, ProductMetadata) and hasattr(member, 'stripe_id')
}
