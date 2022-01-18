from . import ma


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
        )
