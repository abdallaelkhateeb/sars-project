from unittest.mock import patch

from django.test import TestCase

from atms.models import ATM, Service
from routing.services import RoutingEngine


class HaversineFallbackTest(TestCase):

    def setUp(self):
        self.withdrawal_service = Service.objects.create(
            service_id="WITHDRAWAL",
            name=Service.WITHDRAWAL,
        )

        self.atm = ATM.objects.create(
            atm_id="ATM-FALLBACK",
            branch_name="Fallback Test ATM",
            latitude=30.0500,
            longitude=31.2400,
            status=ATM.ONLINE,
            cash_status=ATM.AVAILABLE,
            current_cash_balance=2000,
        )

        self.atm.services.add(self.withdrawal_service)

    @patch("routing.services.MappingGateway.get_distance_and_eta")
    def test_google_maps_failure_uses_haversine_fallback(
        self,
        mock_mapping,
    ):
        mock_mapping.return_value = None

        engine = RoutingEngine()

        results = engine.find_alternatives(
            latitude=30.0444,
            longitude=31.2357,
            requested_service=Service.WITHDRAWAL,
            requested_amount=1000,
        )

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["atmId"],
            "ATM-FALLBACK",
        )

        self.assertEqual(
            results[0]["distanceSource"],
            "HAVERSINE_FALLBACK",
        )

        self.assertGreater(
            results[0]["distanceKm"],
            0,
        )

        self.assertGreater(
            results[0]["etaMinutes"],
            0,
        )