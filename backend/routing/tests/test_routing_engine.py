from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from atms.models import ATM, Service
from routing.services import RoutingEngine


class RoutingEngineCashTest(TestCase):

    def setUp(self):
        self.withdrawal_service = Service.objects.create(
            service_id="WITHDRAWAL",
            name=Service.WITHDRAWAL,
        )

        self.atm = ATM.objects.create(
            atm_id="ATM-001",
            branch_name="Test ATM",
            latitude=30.0444,
            longitude=31.2357,
            status=ATM.ONLINE,
            cash_status=ATM.AVAILABLE,
            current_cash_balance=500,
        )

        self.atm.services.add(self.withdrawal_service)

    def test_atm_with_insufficient_cash_is_excluded(self):
        engine = RoutingEngine()

        candidates = engine.filter_by_cash(
            ATM.objects.filter(atm_id="ATM-001"),
            Service.WITHDRAWAL,
            1000,
        )

        self.assertEqual(
            candidates.count(),
            0,
        )

    def test_atm_with_sufficient_cash_is_kept(self):
        self.atm.current_cash_balance = 1500
        self.atm.save()

        engine = RoutingEngine()

        candidates = engine.filter_by_cash(
            ATM.objects.filter(atm_id="ATM-001"),
            Service.WITHDRAWAL,
            1000,
        )

        self.assertEqual(
            candidates.count(),
            1,
        )

    def test_find_alternatives_returns_atm_with_sufficient_cash(self):
        self.atm.current_cash_balance = 1500
        self.atm.save()

        engine = RoutingEngine()

        results = engine.find_alternatives(
            latitude=30.0440,
            longitude=31.2350,
            requested_service=Service.WITHDRAWAL,
            requested_amount=1000,
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["atmId"],
            "ATM-001",
        )

    @patch(
        "routing.services.MappingGateway.get_distance_and_eta"
    )
    def test_routing_api_returns_suitable_alternative(
        self,
        mock_mapping,
    ):
        """
        Test the routing API with a suitable ATM.
        """

        mock_mapping.return_value = None

        self.atm.current_cash_balance = 1500
        self.atm.save()

        client = APIClient()

        response = client.post(
            "/api/v1/routing/alternatives",
            {
                "latitude": 30.0440,
                "longitude": 31.2350,
                "requestedService": Service.WITHDRAWAL,
                "requestedAmount": 1000,
                "atmId": "ATM-999",
            },
            format="json",
            HTTP_X_API_KEY="sars-local-test-key",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn(
            "alternatives",
            data,
        )

        self.assertEqual(
            len(data["alternatives"]),
            1,
        )

        self.assertEqual(
            data["alternatives"][0]["atmId"],
            "ATM-001",
        )

        self.assertEqual(
            data["alternatives"][0]["distanceSource"],
            "HAVERSINE_FALLBACK",
        )

    @patch(
        "routing.services.MappingGateway.get_distance_and_eta"
    )
    def test_routing_api_excludes_atm_with_insufficient_cash(
        self,
        mock_mapping,
    ):
        """
        An ATM with insufficient cash must not be returned
        for a withdrawal request.
        """

        mock_mapping.return_value = None

        self.atm.current_cash_balance = 500
        self.atm.save()

        client = APIClient()

        response = client.post(
            "/api/v1/routing/alternatives",
            {
                "latitude": 30.0440,
                "longitude": 31.2350,
                "requestedService": Service.WITHDRAWAL,
                "requestedAmount": 1000,
                "atmId": "ATM-999",
            },
            format="json",
            HTTP_X_API_KEY="sars-local-test-key",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn(
            "alternatives",
            data,
        )

        self.assertEqual(
            len(data["alternatives"]),
            0,
        )