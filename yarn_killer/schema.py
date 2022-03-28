from . import ma


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "role")


class ImageSchema(ma.Schema):
    class Meta:
        fields = ("id", "yarn_id", "colorway_id", "url", "label")


multi_image_schema = ImageSchema(many=True)


class FiberSchema(ma.Schema):
    class Meta:
        fields = ("id", "yarn_id", "type", "amount")


multi_fiber_schema = FiberSchema(many=True)


class ColorwaySchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "yarn_id",
            "name",
            "color_broad",
            "color_medium",
            "color_specific",
            "images",
        )

    images = ma.Nested(multi_image_schema)


multi_colorway_schema = ColorwaySchema(many=True)


class StoreSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")


one_store_schema = StoreSchema()


class LinkSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "url",
            "store_id",
            "yarn_id",
            "current_price",
            "price_updated",
            "store",
        )

    store = ma.Nested(one_store_schema)


multi_link_schema = LinkSchema(many=True)


class YarnSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "brand",
            "name",
            "weight_name",
            "gauge",
            "yardage",
            "weight_grams",
            "texture",
            "color_style",
            "discontinued",
            "fibers",
            "colorways",
            "links",
            "images",
        )

    fibers = ma.Nested(multi_fiber_schema)
    colorways = ma.Nested(multi_colorway_schema)
    links = ma.Nested(multi_link_schema)
    images = ma.Nested(multi_image_schema)
