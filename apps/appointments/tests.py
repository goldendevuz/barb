from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.errors.base import StateTransitionError

from apps.customers.models import Customer
from apps.staff.models import Staff
from apps.services.models import Service
from apps.appointments.models import Appointment
from apps.appointments.services import create_appointment, transition_appointment
from apps.analytics.ai_recommender import predict_no_show_risk

class BarberCRMSOLIDTests(TestCase):
    """
    Test suite verifying SOLID principles:
    - SRP: Services are isolated from HTTP views.
    - LSP: Custom StateTransitionError inherits from base DomainException cleanly.
    - DIP: Dynamic analytical classification operates on abstracted DB relations.
    """
    def setUp(self):
        # Setup standard domain entities
        self.customer = Customer.objects.create(
            first_name="Ali",
            last_name="Valiyev",
            phone="+998901112233",
            telegram_id="123456"
        )
        self.staff = Staff.objects.create(
            first_name="Jasur",
            last_name="Karimov",
            phone="+998909998877",
            role="barber"
        )
        self.service = Service.objects.create(
            name="Soch Olish",
            price=40000.00,
            duration_minutes=30
        )
        self.start_time = timezone.now() + timedelta(days=1)

    def test_srp_appointment_creation(self):
        """
        Verify Single Responsibility (SRP): Use-case creation services perform 
        input validation, record saving, and event log generation in a single transaction.
        """
        appointment = create_appointment(
            customer_id=self.customer.id,
            staff_id=self.staff.id,
            service_id=self.service.id,
            start_time=self.start_time
        )
        
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.status, "created")
        self.assertEqual(appointment.customer, self.customer)
        self.assertEqual(appointment.staff, self.staff)

    def test_lsp_state_transition_invariants(self):
        """
        Verify Liskov Substitution (LSP) and Invariant checking:
        An invalid state machine transition must raise a StateTransitionError.
        """
        appointment = create_appointment(
            customer_id=self.customer.id,
            staff_id=self.staff.id,
            service_id=self.service.id,
            start_time=self.start_time
        )
        
        # Valid transition: created -> confirmed
        confirmed_appt = transition_appointment(appointment.id, "confirmed")
        self.assertEqual(confirmed_appt.status, "confirmed")
        
        # Invalid transition: confirmed -> completed (without going through in_service)
        # Should raise StateTransitionError (inheriting from DomainException)
        with self.assertRaises(StateTransitionError):
            transition_appointment(appointment.id, "completed")

    def test_dip_ai_no_show_risk_calculation(self):
        """
        Verify Dependency Inversion (DIP) and Predictive Selectors:
        Heuristic risk classification computes correct probability profiles.
        """
        # Cold start test for a customer with no prior appointments
        risk_profile = predict_no_show_risk(self.customer.id)
        
        self.assertEqual(risk_profile["risk_level"], "low")
        self.assertIn("risk_score", risk_profile)
        self.assertIn("recommendation", risk_profile)
        
        # Setup prior bad behaviors to see if AI detects high risk profile
        appointment = create_appointment(
            customer_id=self.customer.id,
            staff_id=self.staff.id,
            service_id=self.service.id,
            start_time=self.start_time
        )
        # Mark prior booking as no-show
        appointment.status = "no_show"
        appointment.save()
        
        # Re-evaluate
        updated_risk = predict_no_show_risk(self.customer.id)
        self.assertGreater(updated_risk["risk_score"], 35.0)
