from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import UploadImageView, AnalysisResultsView, GeneratecsvReportView,GeneratePdfReportView
urlpatterns = [
    path('upload/', UploadImageView.as_view(), name='image-upload'),
    path('analysis-results/', AnalysisResultsView.as_view(), name='analysis-results'),
    path('generate-csvreport/', GeneratecsvReportView.as_view(), name='generate-csvreport'),
    path('generate-pdfreport/', GeneratePdfReportView.as_view(), name='generate-pdfreport'),
] 

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    