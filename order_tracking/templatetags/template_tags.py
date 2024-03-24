from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Returns the URL-encoded querystring for the current page,
    updating the params with the key/value pairs passed to the tag.

    E.g: given the querystring ?foo=1&bar=2
    {% query_transform bar=3 %} outputs ?foo=1&bar=3
    {% query_transform foo='baz' %} outputs ?foo=baz&bar=2
    {% query_transform foo='one' bar='two' baz=99 %} outputs ?foo=one&bar=two&baz=99

    A RequestContext is required for access to the current querystring.
    """
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return "?" + query.urlencode()

@register.simple_tag(takes_context=True)
def add_to_order_by(context, add, **kwargs):
    """
    If there's not "order_by" in the GET
        add the <add> in
    If it's there AND
        if the <add> ordering is Descending ("-" in order_by)
            Reorient into Ascending (remove "-")
        if the <add> ordering is Ascending (no "-" in order_by)
            Reorient into Descending (add "-")
    If it's there AND <add> isn't in the "order_by"
        Add <add> to order by
    """
    query = context["request"].GET.copy()

    if not "order_by" in query:
        query["order_by"] = add
    elif add.lstrip("-") in query["order_by"]:
        if "-" in add:
            query["order_by"] = query["order_by"].replace(add.lstrip("-"), add)
        else:
            query["order_by"] = query["order_by"].replace(f"-{add}", add)
    else:
        query["order_by"] = query["order_by"] + f",{add}"

    return "?" + query.urlencode()

@register.simple_tag(takes_context=True)
def remove_from_order_by(context, remove, **kwargs):
    query = context["request"].GET.copy()

    if remove in query["order_by"]:
        query["order_by"] = query["order_by"].replace(remove, "").strip(",")

    if not query["order_by"]:
        del query["order_by"]

    return "?" + query.urlencode()
