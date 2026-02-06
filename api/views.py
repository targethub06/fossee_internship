import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import EquipmentDataset, Equipment
from .serializers import EquipmentDatasetSerializer, EquipmentSerializer
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class UploadCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        try:
            df = pd.read_csv(file)
            
            # Basic validation
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": f"CSV must contain columns: {', '.join(required_columns)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create Dataset
            dataset = EquipmentDataset.objects.create(filename=file.name)
            
            # Save Items
            items = []
            for _, row in df.iterrows():
                item = Equipment(
                    dataset=dataset,
                    name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                )
                items.append(item)
            Equipment.objects.bulk_create(items)
            
            # Calculate Summary
            summary = {
                "total_count": len(df),
                "avg_flowrate": df['Flowrate'].mean(),
                "avg_pressure": df['Pressure'].mean(),
                "avg_temperature": df['Temperature'].mean(),
                "type_distribution": df['Type'].value_counts().to_dict()
            }
            dataset.summary_stats = summary
            dataset.save()
            
            # Manage History (Keep last 5)
            all_datasets = EquipmentDataset.objects.all().order_by('-upload_date')
            if all_datasets.count() > 5:
                to_delete = all_datasets[5:]
                for d in to_delete:
                    d.delete()
            
            return Response(EquipmentDatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DatasetHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        datasets = EquipmentDataset.objects.all().order_by('-upload_date')[:5]
        serializer = EquipmentDatasetSerializer(datasets, many=True)
        return Response(serializer.data)

class PDFReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(id=dataset_id)
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 50, f"Equipment Summary Report: {dataset.filename}")
            
            p.setFont("Helvetica", 12)
            y = height - 80
            stats = dataset.summary_stats
            p.drawString(100, y, f"Upload Date: {dataset.upload_date}")
            y -= 20
            p.drawString(100, y, f"Total Equipment: {stats['total_count']}")
            y -= 20
            p.drawString(100, y, f"Avg Flowrate: {stats['avg_flowrate']:.2f}")
            y -= 20
            p.drawString(100, y, f"Avg Pressure: {stats['avg_pressure']:.2f}")
            y -= 20
            p.drawString(100, y, f"Avg Temperature: {stats['avg_temperature']:.2f}")
            
            y -= 40
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y, "Equipment Type Distribution:")
            y -= 20
            p.setFont("Helvetica", 10)
            for etype, count in stats['type_distribution'].items():
                p.drawString(120, y, f"- {etype}: {count}")
                y -= 15
                if y < 50:
                    p.showPage()
                    y = height - 50
            
            p.showPage()
            p.save()
            
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
        except EquipmentDataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)
