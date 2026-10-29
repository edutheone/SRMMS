from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restricts access to users with specific roles.
    """

    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    """
    Administrator only.
    """

    allowed_roles = [
        "ADMIN",
    ]


class SupervisorRequiredMixin(RoleRequiredMixin):
    """
    Administrator and Supervisor.
    """

    allowed_roles = [
        "ADMIN",
        "SUPERVISOR",
    ]


class TechnicianRequiredMixin(RoleRequiredMixin):
    """
    Administrator, Supervisor and Technician.
    """

    allowed_roles = [
        "ADMIN",
        "SUPERVISOR",
        "TECHNICIAN",
    ]


class EmployeeRequiredMixin(RoleRequiredMixin):
    """
    All authenticated users.
    """

    allowed_roles = [
        "ADMIN",
        "SUPERVISOR",
        "TECHNICIAN",
        "EMPLOYEE",
    ]