from rest_framework.pagination import PageNumberPagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20


    """
    page_size 每页数目
    page_query_param 前端发送的页数关键字名，默认为"page"
    page_size_query_param 前端发送的每页数目关键字名，默认为None
    max_page_size 前端最多能设置的每页数量
    """