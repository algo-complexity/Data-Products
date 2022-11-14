from django.shortcuts import get_object_or_404
from ninja import Router

from schemas import PaginatedList, paginate

from . import models, schemas

router = Router()

