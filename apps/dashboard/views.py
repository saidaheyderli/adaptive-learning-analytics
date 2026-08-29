from django.views.generic import TemplateView


class DashboardView(TemplateView):
    """
    Serves the single-page dashboard. All data is fetched client-side
    from the existing DRF API (login, topic-accuracy, recommendations) —
    this view just renders the static shell.
    """
    template_name = 'dashboard/index.html'
