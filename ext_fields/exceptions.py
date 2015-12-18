# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 08:44:44
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals


class ExFieldException(Exception):
    pass


class ExFieldInvalidTypeSet(ExFieldException):
    pass


class ExFieldUnableSaveFieldType(ExFieldException):
    pass


class ExFieldExceptionCannotSet(ExFieldException):
    pass


class ExFieldExceptionCannotDel(ExFieldException):
    pass
