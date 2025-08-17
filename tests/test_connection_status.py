#!/usr/bin/env python3

import os
import sys

# Add project modules path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

from fastwg.core.wireguard import WireGuardManager  # noqa: E402


class TestConnectionStatus(unittest.TestCase):
    """Tests for determining client connection status"""

    def setUp(self):
        """Setup before each test"""
        import tempfile

        temp_dir = tempfile.mkdtemp()
        self.wg_manager = WireGuardManager(config_dir=temp_dir, keys_dir=os.path.join(temp_dir, "keys"))

    def test_parse_handshake_time_seconds(self):
        """Test parsing time in seconds"""
        time_str = "30 seconds ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(seconds=30)
        actual_diff = datetime.now() - parsed_time

        # Check with 5 second tolerance
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 5)

    def test_parse_handshake_time_minutes(self):
        """Test parsing time in minutes"""
        time_str = "2 minutes ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(minutes=2)
        actual_diff = datetime.now() - parsed_time

        # Check with 5 second tolerance
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 5)

    def test_parse_handshake_time_hours(self):
        """Test parsing time in hours"""
        time_str = "1 hour, 30 minutes ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(hours=1, minutes=30)
        actual_diff = datetime.now() - parsed_time

        # Check with 10 second tolerance
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 10)

    def test_parse_handshake_time_days(self):
        """Test parsing time in days"""
        time_str = "2 days, 5 hours ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(days=2, hours=5)
        actual_diff = datetime.now() - parsed_time

        # Check with 60 second tolerance
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 60)

    def test_is_peer_connected_no_handshake(self):
        """Test: peer without handshake is not connected"""
        result = self.wg_manager._is_peer_connected(has_handshake=False, handshake_time=None)
        self.assertFalse(result)

    def test_is_peer_connected_recent_handshake(self):
        """Test: peer with recent handshake is connected"""
        recent_time = datetime.now() - timedelta(minutes=30)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=recent_time)
        self.assertTrue(result)

    def test_is_peer_connected_old_handshake(self):
        """Test: peer with old handshake is not connected"""
        old_time = datetime.now() - timedelta(hours=2)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=old_time)
        self.assertFalse(result)

    def test_is_peer_connected_exact_hour(self):
        """Test: peer with handshake exactly 1 hour ago is not connected (edge case)"""
        exact_hour_time = datetime.now() - timedelta(hours=1)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=exact_hour_time)
        self.assertFalse(result)

    def test_parse_wg_show_output_simple(self):
        """Test parsing simple wg show output"""
        wg_output = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: peer1_key=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: peer2_key=
  allowed ips: 10.0.0.3/32"""

        active_peers = self.wg_manager._parse_wg_show_output(wg_output)

        # Expect only peer1_key as active (30 seconds ago)
        expected = {"peer1_key="}
        self.assertEqual(active_peers, expected)

    def test_parse_wg_show_output_complex(self):
        """Test parsing complex wg show output with different times"""
        wg_output = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: recent_peer=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: old_peer=
  endpoint: 1.2.3.5:1235
  allowed ips: 10.0.0.3/32
  latest handshake: 2 hours ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: no_handshake_peer=
  allowed ips: 10.0.0.4/32"""

        active_peers = self.wg_manager._parse_wg_show_output(wg_output)

        # Expect only recent_peer= as active
        expected = {"recent_peer="}
        self.assertEqual(active_peers, expected)

    def test_parse_wg_show_output_real_data(self):
        """Test with real data from user example"""
        real_wg_output = """interface: wg0
  public key: 6kW4UBw3mEuRBKkpErw7v7SnS335oIlp8Ewk9/6z8zE=
  private key: (hidden)
  listening port: 51820

peer: wzJOQNhUK49H2yAHEGcQNsuEX0t98QMiMpnE7vndRzI=
  endpoint: 5.35.114.145:63557
  allowed ips: 10.42.42.4/32
  latest handshake: 1 minute, 10 seconds ago
  transfer: 1.67 GiB received, 70.31 GiB sent

peer: 8wZQAnND4Gr4QfbYbGIIIhgmtyIpZBtQ3F51TCkSFw8=
  endpoint: 5.35.114.145:37134
  allowed ips: 10.42.42.2/32
  latest handshake: 1 minute, 35 seconds ago
  transfer: 7.85 GiB received, 206.24 GiB sent

peer: 48O/cnQROD4DVLziQB6ZRgPDtgiOto3PK5uVGFv29WA=
  endpoint: 5.35.114.145:52404
  allowed ips: 10.42.42.6/32
  latest handshake: 1 minute, 56 seconds ago
  transfer: 8.99 GiB received, 234.63 GiB sent

peer: towH7ZkYHWNR+alSiRM9El1VjWdM/sxLv6sXM4fQnkU=
  endpoint: 217.107.126.102:6464
  allowed ips: 10.42.42.7/32
  latest handshake: 1 hour, 1 minute, 13 seconds ago
  transfer: 1.11 GiB received, 11.14 GiB sent

peer: 0tYIPr1SUz+M3dUgbom+PVSmKTRgotN1nDfdXeJRkmA=
  allowed ips: 10.42.42.3/32

peer: EYCoo9B7umIJt4tm6noblQsyI6IhiH98bWlxDYyv8QY=
  allowed ips: 10.42.42.8/32"""

        active_peers = self.wg_manager._parse_wg_show_output(real_wg_output)

        # Expect only 3 active peers (with handshake < 1 hour)
        expected = {
            "wzJOQNhUK49H2yAHEGcQNsuEX0t98QMiMpnE7vndRzI=",
            "8wZQAnND4Gr4QfbYbGIIIhgmtyIpZBtQ3F51TCkSFw8=",
            "48O/cnQROD4DVLziQB6ZRgPDtgiOto3PK5uVGFv29WA=",
        }
        self.assertEqual(active_peers, expected)

    @patch("subprocess.run")
    def test_get_active_connections_mock(self, mock_run):
        """Test getting active connections with subprocess mock"""
        # Mock wg show output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: active_peer=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: inactive_peer=
  allowed ips: 10.0.0.3/32"""

        mock_run.return_value = mock_result

        active_peers = self.wg_manager._get_active_connections()

        # Check that subprocess.run was called
        mock_run.assert_called_once_with(["wg", "show"], capture_output=True, text=True)

        # Check result
        expected = {"active_peer="}
        self.assertEqual(active_peers, expected)

    @patch("subprocess.run")
    def test_get_active_connections_error(self, mock_run):
        """Test error handling when getting active connections"""
        # Mock error
        mock_run.side_effect = Exception("Command not found")

        active_peers = self.wg_manager._get_active_connections()

        # Should return empty set on error
        self.assertEqual(active_peers, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
