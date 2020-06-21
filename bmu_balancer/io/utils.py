from marshmallow import Schema, post_load


class PostLoadObjMixin(Schema):

    __model__ = None

    def __new__(cls, *args, **kwargs):
        if not callable(cls.__model__):
            raise RuntimeError(
                f"Schema {repr(cls)} is missing a callable __model__ attribute."
            )
        return super(PostLoadObjMixin, cls).__new__(cls)

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)

    class Meta:
        strict = True
        ordered = True
