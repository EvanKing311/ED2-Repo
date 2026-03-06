from django.db import models
from django.conf import settings  #for CustomUser

#Store parameters each time the user updates them 
class ExperimentSession(models.Model):
    experiment_name = models.CharField(max_length=100)
    parameters = models.JSONField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiment_sessions'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.experiment_name} parameters for {self.user.username}"

#command Model, stores commands sent from the site, timestamp, and user
class Command(models.Model):
    command = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commands', null=True, blank=True) 

    def __str__(self):
        return f"{self.command} (by {self.user.username})"

#Sensor Data model defined but not used in the current iteration of the site, will be better down the line with more readings
class SensorData(models.Model):
    name = models.CharField(max_length=50)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sensor_data', null=True, blank=True)  

    def __str__(self):
        return f"{self.name}: {self.value} @ {self.timestamp}"

#Message model stores messages from Matlab, timestamp, and the user 
class Message(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages') 

    def __str__(self):
        return f"{self.message} @ {self.timestamp} (to {self.user.username})"