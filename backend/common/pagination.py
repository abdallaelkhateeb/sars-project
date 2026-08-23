# backend/common/pagination.py
"""
The API contract's list endpoints (GET /atms, GET /notifications) always
respond with:

    { "data": [...], "meta": { "page", "limit", "total", "totalPages" } }

DRF's default pagination doesn't match that shape or field names out of
the box, hence this. صفية / سارة — reuse this on any other paginated list
endpoint instead of writing a new paginator; keeps every list response
consistent.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "page"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "meta": {
                    "page": self.page.number,
                    "limit": self.get_page_size(self.request),
                    "total": self.page.paginator.count,
                    "totalPages": self.page.paginator.num_pages,
                },
            }
        )