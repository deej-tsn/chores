"""
Tests for the startup readiness and initialization options.

These tests ensure that the on_startup function correctly handles different configuration options:
- Database creation
- Notifications scheduler setup
- Guest user creation (when enabled)
- Test data setup in DEV environment
- Test user creation in DEV environment
- Proper error handling for missing DEV credentials
"""

import pytest
from unittest.mock import patch, MagicMock
from app.main import on_startup
from app.config import Settings


class TestStartupReadiness:
    """Test the on_startup function with various configuration options."""

    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_prod_with_guest_mode_enabled(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables
    ):
        """Test startup in PROD environment with guest mode enabled."""
        # Setup
        settings = Settings(
            environment="PROD",
            disable_guest_mode=False,
            test_user_email="",
            test_user_password="",
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute
        on_startup()

        # Verify
        mock_create_db_and_tables.assert_called_once()
        mock_start_notifications_scheduler.assert_called_once_with(settings)
        mock_create_guest_user.assert_called_once()

    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_prod_with_guest_mode_disabled(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables
    ):
        """Test startup in PROD environment with guest mode disabled."""
        # Setup
        settings = Settings(
            environment="PROD",
            disable_guest_mode=True,
            test_user_email="",
            test_user_password="",
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute
        on_startup()

        # Verify
        mock_create_db_and_tables.assert_called_once()
        mock_start_notifications_scheduler.assert_called_once_with(settings)
        mock_create_guest_user.assert_not_called()

    @patch('app.main.create_test_user')
    @patch('app.main.add_weeks_dates')
    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_dev_with_guest_mode_enabled_and_valid_credentials(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables,
        mock_add_weeks_dates,
        mock_create_test_user
    ):
        """Test startup in DEV environment with guest mode enabled and valid test credentials."""
        # Setup
        settings = Settings(
            environment="DEV",
            disable_guest_mode=False,
            test_user_email="test@example.com",
            test_user_password="password123",
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute
        on_startup()

        # Verify
        mock_create_db_and_tables.assert_called_once()
        mock_start_notifications_scheduler.assert_called_once_with(settings)
        mock_create_guest_user.assert_called_once()
        mock_add_weeks_dates.assert_called_once()
        mock_create_test_user.assert_called_once_with(
            test_email="test@example.com",
            test_password="password123"
        )

    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_dev_with_missing_test_user_email(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables
    ):
        """Test startup in DEV environment with missing test user email."""
        # Setup
        settings = Settings(
            environment="DEV",
            disable_guest_mode=False,
            test_user_email="",  # Empty email
            test_user_password="password123",
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute & Verify
        with pytest.raises(KeyError, match="No 'TEST_USER_EMAIL' found in env"):
            on_startup()

    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_dev_with_missing_test_user_password(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables
    ):
        """Test startup in DEV environment with missing test user password."""
        # Setup
        settings = Settings(
            environment="DEV",
            disable_guest_mode=False,
            test_user_email="test@example.com",
            test_user_password="",  # Empty password
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute & Verify
        with pytest.raises(KeyError, match="No 'TEST_USER_PASSWORD' found in env"):
            on_startup()

    @patch('app.main.create_test_user')
    @patch('app.main.add_weeks_dates')
    @patch('app.main.create_db_and_tables')
    @patch('app.main.start_notifications_scheduler')
    @patch('app.main.create_guest_user')
    @patch('app.main.get_settings')
    def test_dev_with_guest_mode_disabled_and_valid_credentials(
        self,
        mock_get_settings,
        mock_create_guest_user,
        mock_start_notifications_scheduler,
        mock_create_db_and_tables,
        mock_add_weeks_dates,
        mock_create_test_user
    ):
        """Test startup in DEV environment with guest mode disabled and valid test credentials."""
        # Setup
        settings = Settings(
            environment="DEV",
            disable_guest_mode=True,
            test_user_email="test@example.com",
            test_user_password="password123",
            secret_key="test",
            resend_api_key="test"
        )
        mock_get_settings.return_value = settings

        # Execute
        on_startup()

        # Verify
        mock_create_db_and_tables.assert_called_once()
        mock_start_notifications_scheduler.assert_called_once_with(settings)
        mock_create_guest_user.assert_not_called()
        mock_add_weeks_dates.assert_called_once()
        mock_create_test_user.assert_called_once_with(
            test_email="test@example.com",
            test_password="password123"
        )