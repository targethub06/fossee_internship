from django.db import models

class EquipmentDataset(models.Model):
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    summary_stats = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.filename} - {self.upload_date}"

class Equipment(models.Model):
    dataset = models.ForeignKey(EquipmentDataset, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return self.name
