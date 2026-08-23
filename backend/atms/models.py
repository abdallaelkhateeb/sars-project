import uuid
from django.db import models


class Service(models.Model):
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    CURRENCY_EXCHANGE = "CURRENCY_EXCHANGE"
    CHECK_DEPOSIT = "CHECK_DEPOSIT"

    SERVICE_CHOICES = [
        (WITHDRAWAL, "Withdrawal"),
        (DEPOSIT, "Deposit"),
        (CURRENCY_EXCHANGE, "Currency Exchange"),
        (CHECK_DEPOSIT, "Check Deposit"),
    ]

    service_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=50, choices=SERVICE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class ATM(models.Model):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    STATUS_CHOICES = [
        (ONLINE, "Online"),
        (OFFLINE, "Offline"),
        (MAINTENANCE, "Maintenance"),
    ]

    AVAILABLE = "AVAILABLE"
    LOW = "LOW"
    EMPTY = "EMPTY"
    CASH_STATUS_CHOICES = [
        (AVAILABLE, "Available"),
        (LOW, "Low"),
        (EMPTY, "Empty"),
    ]

    atm_id = models.CharField(primary_key=True, max_length=50)
    branch_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OFFLINE)
    cash_status = models.CharField(max_length=20, choices=CASH_STATUS_CHOICES, default=EMPTY)
    current_cash_balance = models.FloatField(default=0)
    services = models.ManyToManyField(Service, through="ATMService", related_name="atms")
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["cash_status"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def has_sufficient_cash(self, requested_amount, buffer_amount=0):
        """
        Used by RoutingEngine's cash-sufficiency filter:
        current_cash_balance >= requested_amount + buffer_amount
        """
        if requested_amount is None:
            return True
        return self.current_cash_balance >= (requested_amount + buffer_amount)

    def get_supported_services(self):
        return list(self.services.values_list("name", flat=True))

    def __str__(self):
        return f"{self.atm_id} — {self.branch_name}"


class ATMService(models.Model):
    atm = models.ForeignKey(ATM, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("atm", "service")


class HeartbeatLog(models.Model):
    heartbeat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    atm = models.ForeignKey(ATM, on_delete=models.CASCADE, related_name="heartbeats")
    status = models.CharField(max_length=20, choices=ATM.STATUS_CHOICES)
    cash_status = models.CharField(max_length=20, choices=ATM.CASH_STATUS_CHOICES)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        indexes = [models.Index(fields=["atm", "-received_at"])]
