# views.py
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UploadedImage
from .serializers import UploadedImageSerializer,AnalysisSerializer
from .utils import analyze_exif_data, generate_csv_report,get_image_metadata,generate_pdf_report
from django.conf import settings

from rest_framework.request import Request
from reportlab.pdfgen import canvas
import os
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'


class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = UploadedImageSerializer(data=request.data)
            if serializer.is_valid():
                uploaded_image = serializer.save()
                metadata = get_image_metadata(uploaded_image.image)
                uploaded_image.height = metadata.get('height')
                uploaded_image.width = metadata.get('width')
                uploaded_image.analyzed = True
                uploaded_image.save()
                analyze_exif_data(uploaded_image)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalysisResultsView(APIView):
    pagination_class = CustomPageNumberPagination
    def get(self, request: Request, *args, **kwargs):
        try:
            images = UploadedImage.objects.all()
            search_query = request.query_params.get('search')
            if search_query:
                images = images.filter(
                    Q(image__icontains=search_query) | 
                    Q(height=search_query) |          
                    Q(width=search_query) |
                    Q(speed=search_query)             
                )
            paginator = Paginator(images, self.pagination_class.page_size)
            page_number = request.query_params.get('page', 1)
            if page_number is not None:  
                page_number = int(page_number)
            else:
                page_number = 1  
            page_obj = paginator.get_page(page_number)
            for image in page_obj:
                image.image_url = request.build_absolute_uri(settings.MEDIA_URL + str(image.image))
            serializer = AnalysisSerializer(page_obj, many=True)
            return Response({
                'count': paginator.count,
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'results': serializer.data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GeneratecsvReportView(APIView):
    def get(self, request, *args, **kwargs):
        format = request.query_params.get('format', 'csv')
        images = UploadedImage.objects.all()
        serializer = AnalysisSerializer(images, many=True)
        if format == 'csv':
            report = generate_csv_report(serializer.data)
            response = Response(report, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="analysis_report.csv"'
            return response
        else:
            return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)
    



class GeneratePdfReportView(APIView):
   
    def save_pdf_report(self, report, folder_path, file_name):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(report)
        return file_path

    def get(self, request, *args, **kwargs):
        format = request.query_params.get('format', 'pdf')
        images = UploadedImage.objects.all()
        serializer = AnalysisSerializer(images, many=True)
        if format == 'pdf':
            report = generate_pdf_report(serializer.data)
            # content_type = 'application/pdf'
            # file_extension = 'pdf'
            folder_path = 'media/pdf_reports' 
            file_name = 'analysis_report.pdf'  
            file_path = self.save_pdf_report(report, folder_path, file_name)
            return Response({"message": f"PDF report saved at {file_path}"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)