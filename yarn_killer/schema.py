from . import ma


class FiberSchema(ma.Schema):
    class Meta:
        fields = ("id", "yarn_id", "type", "amount")


multi_fiber_schema = FiberSchema(many=True)


class ColorwaySchema(ma.Schema):
    class Meta:
        fields = ("id", "yarn_id", "name", "color_broad", "color_medium", "color_specific")


multi_colorway_schema = ColorwaySchema(many=True)


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
        )

    fibers = ma.Nested(multi_fiber_schema)
    colorways = ma.Nested(multi_colorway_schema)
