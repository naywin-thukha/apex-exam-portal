from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """Anonymous -> redirected to login. Wrong role -> 403. Right role -> allowed."""
    allowed_roles = ()   # each view overrides this

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role not in self.allowed_roles:
            raise PermissionDenied          # 403
        return super().dispatch(request, *args, **kwargs)