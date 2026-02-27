from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src: str, context: dict, filename: str = "report.pdf") -> HttpResponse:
    template = get_template(template_src)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    status = pisa.CreatePDF(html, dest=response)
    if status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response