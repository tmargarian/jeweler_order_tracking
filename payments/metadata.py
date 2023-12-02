from dataclasses import dataclass
import features


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
    is_default=True,
    feature_list=[
        features.PRIORITY_SUPPORT,
        features.SMS_NOTIFICATIONS,
        features.PRIORITY_SUPPORT,
    ],
)
