import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os

from fastwg.core.wireguard import WireGuardManager
from fastwg.models.server import Server


class TestServerInit(unittest.TestCase):
    """Test server initialization functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "wireguard")
        os.makedirs(self.config_dir, exist_ok=True)

        # Mock database
        self.mock_db = MagicMock()
        self.mock_db.get_server_config.return_value = None
        self.mock_db.save_server_config.return_value = True

        # Create WireGuardManager with mocked database
        with patch("fastwg.core.wireguard.Database") as mock_database_class:
            mock_database_class.return_value = self.mock_db
            self.wg_manager = WireGuardManager(config_dir=self.config_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.chmod")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_private_key")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_public_key")
    def test_init_server_config_success(
        self, mock_generate_public, mock_generate_private, mock_chmod, mock_open
    ):
        """Test successful server configuration initialization"""
        # Setup mocks
        mock_generate_private.return_value = "test_private_key"
        mock_generate_public.return_value = "test_public_key"

        # Call the method
        result = self.wg_manager.init_server_config(
            interface="wg0", port=51820, network="10.42.42.0/24", dns="8.8.8.8"
        )

        # Assertions
        self.assertTrue(result)

        # Check that file was written
        mock_open.assert_called_once()
        written_content = mock_open().write.call_args[0][0]

        # Check config content
        self.assertIn("[Interface]", written_content)
        self.assertIn("PrivateKey = test_private_key", written_content)
        self.assertIn("Address = 10.42.42.0/24", written_content)
        self.assertIn("ListenPort = 51820", written_content)
        self.assertIn("DNS = 8.8.8.8", written_content)
        self.assertIn("PostUp = iptables", written_content)
        self.assertIn("PostDown = iptables", written_content)

        # Check file permissions
        mock_chmod.assert_called_once()

        # Check database calls
        self.mock_db.get_server_config.assert_called_once()
        self.mock_db.save_server_config.assert_called_once()

        # Check Server object creation
        saved_server = self.mock_db.save_server_config.call_args[0][0]
        self.assertIsInstance(saved_server, Server)
        self.assertEqual(saved_server.interface, "wg0")
        self.assertEqual(saved_server.port, 51820)
        self.assertEqual(saved_server.address, "10.42.42.0/24")
        self.assertEqual(saved_server.dns, "8.8.8.8")
        self.assertEqual(saved_server.mtu, 1420)
        self.assertEqual(
            saved_server.config_path, os.path.join(self.config_dir, "wg0.conf")
        )
        self.assertIsNone(saved_server.external_ip)

    def test_init_server_config_already_exists(self):
        """Test that init fails if server config already exists"""
        # Setup mock to return existing config
        self.mock_db.get_server_config.return_value = MagicMock()

        # Call the method
        result = self.wg_manager.init_server_config()

        # Assertions
        self.assertFalse(result)
        self.mock_db.get_server_config.assert_called_once()
        self.mock_db.save_server_config.assert_not_called()

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_init_server_config_file_error(self, mock_open):
        """Test that init fails on file write error"""
        # Call the method
        result = self.wg_manager.init_server_config()

        # Assertions
        self.assertFalse(result)
        self.mock_db.save_server_config.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.chmod")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_private_key")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_public_key")
    def test_init_server_config_database_error(
        self, mock_generate_public, mock_generate_private, mock_chmod, mock_open
    ):
        """Test that init fails on database save error"""
        # Setup mocks
        mock_generate_private.return_value = "test_private_key"
        mock_generate_public.return_value = "test_public_key"
        self.mock_db.save_server_config.return_value = False

        # Call the method
        result = self.wg_manager.init_server_config()

        # Assertions
        self.assertFalse(result)
        self.mock_db.save_server_config.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.chmod")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_private_key")
    @patch("fastwg.core.wireguard.WireGuardManager._generate_public_key")
    def test_init_server_config_custom_parameters(
        self, mock_generate_public, mock_generate_private, mock_chmod, mock_open
    ):
        """Test init with custom parameters"""
        # Setup mocks
        mock_generate_private.return_value = "test_private_key"
        mock_generate_public.return_value = "test_public_key"

        # Call the method with custom parameters
        result = self.wg_manager.init_server_config(
            interface="wg1", port=51821, network="192.168.1.0/24", dns="1.1.1.1"
        )

        # Assertions
        self.assertTrue(result)

        # Check written content
        written_content = mock_open().write.call_args[0][0]
        self.assertIn("Address = 192.168.1.0/24", written_content)
        self.assertIn("ListenPort = 51821", written_content)
        self.assertIn("DNS = 1.1.1.1", written_content)

        # Check Server object
        saved_server = self.mock_db.save_server_config.call_args[0][0]
        self.assertEqual(saved_server.interface, "wg1")
        self.assertEqual(saved_server.port, 51821)
        self.assertEqual(saved_server.address, "192.168.1.0/24")
        self.assertEqual(saved_server.dns, "1.1.1.1")


if __name__ == "__main__":
    unittest.main()
