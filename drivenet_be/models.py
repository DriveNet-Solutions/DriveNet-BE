from django.db import models


class Client(models.Model):
    id_u = models.AutoField(primary_key=True, verbose_name="ID Usuario")
    id = models.IntegerField(unique=True, verbose_name="Identificación (Cédula)")
    name = models.CharField(max_length=100, verbose_name="Nombre completo")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    password = models.CharField(max_length=255, verbose_name="Contraseña")
    registration_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Registro")
    assigned_agent = models.IntegerField(null=True, blank=True, verbose_name="Agente Asignado")

    class Meta:
        db_table = 'user'
        constraints = [
            models.UniqueConstraint(fields=['id'], name='unique_id'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]
        indexes = [
            models.Index(fields=['id'], name='id_index'),
            models.Index(fields=['email'], name='email_index'),
        ]

    def __str__(self):
        return f"{self.name} ({self.id})"
