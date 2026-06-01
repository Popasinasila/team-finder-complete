from django.core.paginator import Paginator

PROJECTS_PER_PAGE = 12


def paginate_queryset(queryset, page_number, per_page=PROJECTS_PER_PAGE):
    """Return a page object for the given queryset and page number."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
