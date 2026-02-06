from django.urls import path
from .views import UploadCSVView, DatasetHistoryView, PDFReportView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='csv-upload'),
    path('history/', DatasetHistoryView.as_view(), name='dataset-history'),
    path('report/<int:dataset_id>/', PDFReportView.as_view(), name='pdf-report'),
]
