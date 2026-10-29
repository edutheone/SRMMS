
import json
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from assets.models import Asset
from requests_app.models import ServiceRequest
from workorders.models import WorkOrder


class ChatbotView(LoginRequiredMixin, TemplateView):
    template_name = "chatbot/chat.html"


@method_decorator(csrf_protect, name="dispatch")
class ChatbotMessageView(LoginRequiredMixin, View):
    """Secure, rule-based SRMMS assistant."""

    MAX_MESSAGE_LENGTH = 1000

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Invalid message data."},
                status=400,
            )

        if not isinstance(data, dict):
            return JsonResponse(
                {"error": "Invalid message data."},
                status=400,
            )

        message = data.get("message", "")

        if not isinstance(message, str):
            return JsonResponse(
                {"error": "Message must be text."},
                status=400,
            )

        message = message.strip()

        if not message:
            return JsonResponse(
                {"error": "Please enter a message."},
                status=400,
            )

        if len(message) > self.MAX_MESSAGE_LENGTH:
            return JsonResponse(
                {"error": "Message must be 1000 characters or fewer."},
                status=400,
            )

        response = self.get_srmms_response(message, request.user)

        return JsonResponse({
            "message": message,
            "response": response,
        })

    @staticmethod
    def normalize_message(message):
        question = message.lower().strip()
        question = re.sub(r"[^\w\s'-]", " ", question)
        question = re.sub(r"\s+", " ", question)
        return question.strip()

    @staticmethod
    def contains_phrase(question, phrases):
        return any(
            re.search(
                rf"(?<!\w){re.escape(phrase)}(?!\w)",
                question,
            )
            for phrase in phrases
        )

    @staticmethod
    def extract_identifier(question, patterns):
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip(" .,:;")
        return None

    # ---------------------------------------------------------
    # ROLE-AWARE QUERYSETS
    # ---------------------------------------------------------

    def get_service_request_queryset(self, user):
        role = getattr(user, "role", None)

        if role in ["ADMIN", "SUPERVISOR"]:
            return ServiceRequest.objects.all()

        if role == "EMPLOYEE":
            return ServiceRequest.objects.filter(requester=user)

        if role == "TECHNICIAN":
            return ServiceRequest.objects.filter(assigned_to=user)

        return ServiceRequest.objects.none()

    def get_work_order_queryset(self, user):
        role = getattr(user, "role", None)

        if role in ["ADMIN", "SUPERVISOR"]:
            return WorkOrder.objects.all()

        if role == "TECHNICIAN":
            return WorkOrder.objects.filter(assigned_to=user)

        if role == "EMPLOYEE":
            return WorkOrder.objects.filter(
                service_request__requester=user
            )

        return WorkOrder.objects.none()

    def get_asset_queryset(self, user):
        role = getattr(user, "role", None)

        queryset = Asset.objects.select_related(
            "category",
            "department",
        )

        if role in ["ADMIN", "SUPERVISOR"]:
            return queryset

        if role == "TECHNICIAN":
            work_order_assets = self.get_work_order_queryset(
                user
            ).values_list("asset_id", flat=True)

            request_assets = self.get_service_request_queryset(
                user
            ).values_list("asset_id", flat=True)

            return queryset.filter(
                Q(pk__in=work_order_assets)
                | Q(pk__in=request_assets)
            ).distinct()

        if role == "EMPLOYEE":
            request_assets = self.get_service_request_queryset(
                user
            ).values_list("asset_id", flat=True)

            return queryset.filter(
                pk__in=request_assets
            ).distinct()

        return queryset.none()

    # ---------------------------------------------------------
    # IDENTIFIER EXTRACTION
    # ---------------------------------------------------------

    def extract_request_number(self, question):
        return self.extract_identifier(
            question,
            [
                r"\brequest\s+number\s*[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\bservice\s+request\s+(?:number\s*)?[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\b(SR[-/][a-z0-9/-]+)\b",
            ],
        )

    def extract_work_order_number(self, question):
        return self.extract_identifier(
            question,
            [
                r"\bwork\s+order\s+number\s*[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\bwork\s+order\s+(?:number\s*)?[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\b(WO[-/][a-z0-9/-]+)\b",
            ],
        )

    def extract_asset_identifier(self, question):
        return self.extract_identifier(
            question,
            [
                r"\basset\s+tag\s*[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\btag\s+(?:number\s*)?[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\bserial\s+(?:number\s*)?[:#-]?\s*([a-z0-9][a-z0-9/-]*)",
                r"\bserial\s*[:#-]\s*([a-z0-9][a-z0-9/-]*)",
                r"\basset\s+(?:number\s*)?[:#-]\s*([a-z0-9][a-z0-9/-]*)",
            ],
        )

    # ---------------------------------------------------------
    # GENERIC STATUS STATISTICS
    # ---------------------------------------------------------

    def get_status_statistics(
        self,
        queryset,
        model,
        question,
        record_name,
    ):
        """
        Count every status defined by a model and answer a specific
        status question or return a complete status summary.
        """

        status_field = model._meta.get_field("status")
        status_choices = status_field.choices

        status_counts = []

        for status_value, status_label in status_choices:
            count = queryset.filter(
                status=status_value
            ).count()

            status_counts.append({
                "value": status_value,
                "label": str(status_label),
                "count": count,
            })

        # Find a status explicitly mentioned in the question.
        # Prefer the longest matching label to avoid ambiguous matches.
        matching_statuses = []

        for item in status_counts:
            label = item["label"].lower().replace("_", " ").replace("-", " ")
            value = item["value"].lower().replace("_", " ").replace("-", " ")

            if self.contains_phrase(question, [label, value]):
                matching_statuses.append(item)

        if matching_statuses:
            selected_status = max(
                matching_statuses,
                key=lambda item: max(
                    len(item["label"]),
                    len(item["value"]),
                ),
            )

            return (
                f"{record_name} with status "
                f"'{selected_status['label']}': "
                f"{selected_status['count']}."
            )

        total = queryset.count()

        lines = [
            f"Total {record_name.lower()}: {total}",
            "",
            "Breakdown by status:",
        ]

        for item in status_counts:
            lines.append(
                f"{item['label']}: {item['count']}"
            )

        return "\n".join(lines)

    def get_request_statistics(self, question, user):
        return self.get_status_statistics(
            queryset=self.get_service_request_queryset(user),
            model=ServiceRequest,
            question=question,
            record_name="Service requests",
        )

    def get_work_order_statistics(self, question, user):
        return self.get_status_statistics(
            queryset=self.get_work_order_queryset(user),
            model=WorkOrder,
            question=question,
            record_name="Work orders",
        )

    # ---------------------------------------------------------
    # SERVICE REQUEST DETAILS
    # ---------------------------------------------------------

    def get_request_details(self, request_number, user):
        item = self.get_service_request_queryset(
            user
        ).filter(
            request_number__iexact=request_number
        ).select_related(
            "requester",
            "department",
            "asset",
            "assigned_to",
        ).first()

        if not item:
            return (
                f"I couldn't find service request '{request_number}' "
                "in the records available to your account. "
                "Please check the request number."
            )

        technician = (
            item.assigned_to.get_full_name()
            or item.assigned_to.username
            if item.assigned_to
            else "Not assigned"
        )

        return (
            f"Service Request: {item.request_number}\n"
            f"Title: {item.title}\n"
            f"Status: {item.get_status_display()}\n"
            f"Priority: {item.get_priority_display()}\n"
            f"Department: {item.department}\n"
            f"Location: {item.location}\n"
            f"Asset: {item.asset or 'Not specified'}\n"
            f"Assigned technician: {technician}\n"
            f"Date submitted: {item.date_submitted}\n"
            f"Date resolved: {item.date_resolved or 'Not resolved'}"
        )

    # ---------------------------------------------------------
    # WORK ORDER DETAILS
    # ---------------------------------------------------------

    def get_work_order_details(self, work_order_number, user):
        item = self.get_work_order_queryset(
            user
        ).filter(
            work_order_number__iexact=work_order_number
        ).select_related(
            "service_request",
            "asset",
            "department",
            "assigned_to",
        ).first()

        if not item:
            return (
                f"I couldn't find work order '{work_order_number}' "
                "in the records available to your account. "
                "Please check the work order number."
            )

        technician = (
            item.assigned_to.get_full_name()
            or item.assigned_to.username
            if item.assigned_to
            else "Not assigned"
        )

        return (
            f"Work Order: {item.work_order_number}\n"
            f"Title: {item.title}\n"
            f"Status: {item.get_status_display()}\n"
            f"Priority: {item.get_priority_display()}\n"
            f"Service Request: {item.service_request or 'Not linked'}\n"
            f"Department: {item.department}\n"
            f"Location: {item.location}\n"
            f"Asset: {item.asset or 'Not specified'}\n"
            f"Assigned technician: {technician}\n"
            f"Scheduled date: {item.scheduled_date or 'Not scheduled'}\n"
            f"Completed date: {item.completed_date or 'Not completed'}\n"
            f"Completion notes: "
            f"{item.completion_notes or 'No completion notes yet'}"
        )

    # ---------------------------------------------------------
    # ASSET DETAILS
    # ---------------------------------------------------------

    def get_asset_details(self, identifier, user, question):
        queryset = self.get_asset_queryset(user)

        if self.contains_phrase(question, ["serial", "serial number"]):
            item = queryset.filter(
                serial_number__iexact=identifier
            ).first()
        else:
            item = queryset.filter(
                asset_tag__iexact=identifier
            ).first()

            if not item:
                item = queryset.filter(
                    serial_number__iexact=identifier
                ).first()

        if not item:
            return (
                f"I couldn't find asset '{identifier}' among the assets "
                "available to your account. Check the asset tag or "
                "serial number, or contact your administrator."
            )

        return (
            f"Asset Details\n"
            f"Asset tag: {item.asset_tag}\n"
            f"Name: {item.name}\n"
            f"Serial number: {item.serial_number or 'Not recorded'}\n"
            f"Category: {item.category.name}\n"
            f"Department: {item.department}\n"
            f"Location: {item.location}\n"
            f"Status: {item.get_status_display()}\n"
            f"Purchase date: {item.purchase_date or 'Not recorded'}\n"
            f"Warranty expiry: {item.warranty_expiry or 'Not recorded'}\n"
            f"Description: {item.description or 'No description provided'}"
        )

    # ---------------------------------------------------------
    # MAIN RESPONSE ROUTER
    # ---------------------------------------------------------

    def get_srmms_response(self, message, user):
        question = self.normalize_message(message)

        # Specific work order lookup.
        work_order_number = self.extract_work_order_number(question)

        if work_order_number:
            return self.get_work_order_details(
                work_order_number,
                user,
            )

        # Specific service request lookup.
        request_number = self.extract_request_number(question)

        if request_number:
            return self.get_request_details(
                request_number,
                user,
            )

        # Specific asset lookup.
        asset_identifier = self.extract_asset_identifier(question)

        if asset_identifier:
            return self.get_asset_details(
                asset_identifier,
                user,
                question,
            )

        # Detect whether the question concerns work-order statistics.
        work_order_topic = self.contains_phrase(
            question,
            [
                "work order",
                "work orders",
                "workorder",
                "workorders",
            ],
        )

        status_question = self.contains_phrase(
            question,
            [
                "how many",
                "count",
                "statistics",
                "summary",
                "all status",
                "all statuses",
                "by status",
                "status breakdown",
                "total",
                "completed",
                "complete",
                "pending",
                "assigned",
                "in progress",
                "cancelled",
                "canceled",
            ],
        )

        if work_order_topic and status_question:
            return self.get_work_order_statistics(
                question,
                user,
            )

        # Service-request statistics.
        request_topic = self.contains_phrase(
            question,
            [
                "request",
                "requests",
                "service request",
                "service requests",
            ],
        )

        if request_topic and status_question:
            return self.get_request_statistics(
                question,
                user,
            )

        # Greetings.
        if self.contains_phrase(
            question,
            [
                "hello",
                "hi",
                "hey",
                "good morning",
                "good afternoon",
                "good evening",
            ],
        ):
            return (
                f"Hello {user.get_full_name() or user.username}! "
                "I'm your SRMMS assistant. I can help you check service "
                "requests, work orders, assets, and system features. "
                "What would you like to know?"
            )

        # Help: explain the SRMMS features the chatbot currently supports.
        if self.contains_phrase(
            question,
            [
                "help",
                "what can you do",
                "what can you help with",
                "how do i use you",
                "your features",
                "chatbot features",
                "features",
            ],
        ):
            return (
                "I am your SRMMS assistant, and I am still under development. "
                "I can currently help with information related to the Service "
                "Request and Maintenance Management System (SRMMS), including:\n"
                "- Service request details and status summaries\n"
                "- Work order details and status summaries\n"
                "- Asset lookups using an asset tag or serial number\n"
                "- General guidance on service requests, work orders, assets, "
                "notifications, reports, login, profiles, and roles\n"
                "- Information only from records your account is permitted to access\n\n"
                "Examples you can ask:\n"
                "- Show all service request statuses\n"
                "- How many completed requests?\n"
                "- Show all work order statuses\n"
                "- How many work orders are cancelled?\n"
                "- Show work order WO-001\n"
                "- Show request SR-001\n"
                "- Show asset tag AST-001\n"
                "- Show serial number SN-001\n"
                "- How do I create a service request?\n\n"
                "Replace sample identifiers with real identifiers from your system. "
                "I cannot reliably answer questions outside SRMMS or features that "
                "have not yet been implemented."
            )

        # Asset guidance.
        if self.contains_phrase(
            question,
            ["asset", "assets", "inventory", "serial number", "asset tag"],
        ):
            return (
                "I can look up assets by asset tag or serial number. "
                "For example, ask 'Show asset tag AST-001' or "
                "'Show serial number SN-001'. "
                "The results depend on your role and permitted records."
            )

        # Service request guidance.
        if self.contains_phrase(
            question,
            [
                "service request",
                "service requests",
                "raise a request",
                "create a request",
            ],
        ):
            return (
                "Service requests let you report an ICT issue or request "
                "maintenance. Open the Service Requests section, create "
                "a request, provide its details and priority, then submit "
                "it. Available actions depend on your role."
            )

        # Work order guidance.
        if self.contains_phrase(
            question,
            ["work order", "work orders", "workorder", "workorders"],
        ):
            return (
                "Work orders track maintenance work assigned to technicians. "
                "You can ask 'Show all work order statuses' or "
                "'How many work orders are completed?' to get a status "
                "summary, or provide a work order number for its details."
            )

        # Maintenance guidance.
        if self.contains_phrase(
            question,
            ["maintenance", "repair", "service history"],
        ):
            return (
                "SRMMS tracks maintenance through service requests and "
                "work orders. Check the Maintenance or Work Orders section "
                "available in your account for relevant records."
            )

        # Notification guidance.
        if self.contains_phrase(
            question,
            ["notification", "notifications", "alert", "alerts"],
        ):
            return (
                "Open the notification bell or Notifications page to "
                "view alerts available to your account."
            )

        # Feedback guidance.
        if self.contains_phrase(
            question,
            ["feedback", "rate", "rating", "comment"],
        ):
            return (
                "Use the Feedback section to submit feedback if it is "
                "available in your account."
            )

        # Reports guidance.
        if self.contains_phrase(
            question,
            ["report", "reports", "analytics"],
        ):
            return (
                "Open the Reports section to view the reports available "
                "to your role."
            )

        # Login and password guidance.
        if self.contains_phrase(
            question,
            [
                "login",
                "log in",
                "sign in",
                "password",
                "forgot password",
                "reset password",
            ],
        ):
            return (
                "Use your registered credentials to sign in. If you "
                "forgot your password, use the password reset option "
                "if enabled, or contact your administrator."
            )

        # Profile guidance.
        if self.contains_phrase(
            question,
            ["profile", "my account", "phone number", "profile photo"],
        ):
            return (
                "Open your profile or account section to review or update "
                "the details available to you."
            )

        # Roles and permissions.
        if self.contains_phrase(
            question,
            [
                "role",
                "permission",
                "permissions",
                "administrator",
                "supervisor",
                "technician",
                "employee",
            ],
        ):
            return (
                "SRMMS has Administrator, Supervisor, Technician, and "
                "Employee roles. The records available to you depend "
                "on your assigned role."
            )

        # Fallback for unsupported, unrelated, or not-yet-implemented questions.
        return (
            "I am under development. I can only help you with information "
            "related to SRMMS (Service Request and Maintenance Management System).\n\n"
            "Here is what I can currently help you with:\n"
            "- Check service request details and status summaries\n"
            "- Check work order details and status summaries\n"
            "- Look up assets using an asset tag or serial number\n"
            "- Explain how to use service requests, work orders, assets, "
            "notifications, reports, login, profiles, and roles\n"
            "- Answer using records your account is authorized to access\n\n"
            "Try asking 'help', 'How many completed requests?', "
            "'Show all work order statuses', 'Show request SR-001', "
            "or 'Show asset tag AST-001'. Replace sample identifiers with "
            "real identifiers from your system. If a feature is not yet "
            "implemented, I will not be able to provide that information."
        )
