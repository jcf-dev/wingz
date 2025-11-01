from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LimitedPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that enforces a maximum page size limit
    to prevent resource exhaustion attacks.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100  # Maximum allowed page size

    def get_paginated_response(self, data):
        """Return paginated response with metadata"""
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.page_size,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
            }
        )
