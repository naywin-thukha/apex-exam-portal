from django.test import TestCase
from django.urls import reverse

from .models import User

PAGES = {
    "accounts:admin_dashboard": User.Role.ADMIN,
    "accounts:teacher_dashboard": User.Role.TEACHER,
    "accounts:student_dashboard": User.Role.STUDENT,
}


class RoleAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {
            role: User.objects.create_user(username=role, password="Str0ng-pass-123", role=role)
            for role in User.Role.values
        }

    def test_anonymous_redirected_to_login(self):
        for name in PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse(name)}")

    def test_wrong_role_gets_403(self):
        for name, owner_role in PAGES.items():
            for role, user in self.users.items():
                if role == owner_role:
                    continue
                with self.subTest(page=name, role=role):
                    self.client.force_login(user)
                    self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_correct_role_gets_200(self):
        for name, owner_role in PAGES.items():
            with self.subTest(page=name):
                self.client.force_login(self.users[owner_role])
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)


class LoginFlowTests(TestCase):
    def test_each_role_lands_on_own_dashboard(self):
        for role, name in [
            (User.Role.ADMIN, "accounts:admin_dashboard"),
            (User.Role.TEACHER, "accounts:teacher_dashboard"),
            (User.Role.STUDENT, "accounts:student_dashboard"),
        ]:
            with self.subTest(role=role):
                User.objects.create_user(username=f"u_{role}", password="Str0ng-pass-123", role=role)
                response = self.client.post(
                    reverse("accounts:login"),
                    {"username": f"u_{role}", "password": "Str0ng-pass-123"},
                    follow=True,
                )
                self.assertRedirects(response, reverse(name))
                self.client.logout()

    def test_inactive_account_cannot_log_in(self):
        User.objects.create_user(username="old", password="Str0ng-pass-123", is_active=False)
        response = self.client.post(
            reverse("accounts:login"), {"username": "old", "password": "Str0ng-pass-123"}
        )
        self.assertEqual(response.status_code, 200)          # login page shown again
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_no_public_signup_page(self):
        self.assertEqual(self.client.get("/accounts/signup/").status_code, 404)