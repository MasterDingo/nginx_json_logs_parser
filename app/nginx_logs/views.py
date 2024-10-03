from django.shortcuts import redirect, reverse  # type: ignore[attr-defined]


def main_page(request):
    """Main page view."""
    return redirect(reverse("api-v1-swagger-ui"))
