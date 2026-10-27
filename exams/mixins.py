from accounts.models import User
from accounts.permissions import RoleRequiredMixin


class TeacherRequiredMixin(RoleRequiredMixin):
    """Job: only logged-in teachers get through."""

    allowed_roles = (User.Role.TEACHER,)