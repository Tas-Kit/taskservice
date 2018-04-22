from rest_framework import schemas
import coreapi


class Schema(schemas.AutoSchema):

    def get_manual_fields(self, path, method):
        return [field for field in self._manual_fields if field.method == method or field.method is None]
        # return self._manual_fields


class Field(coreapi.Field):

    def __new__(cls,
                field_name,
                method=None,
                required=False,
                location=None,
                schema=None):
        inst = coreapi.Field.__new__(cls,
                                     field_name,
                                     required=required,
                                     location=location,
                                     schema=schema)
        inst.method = method
        return inst
