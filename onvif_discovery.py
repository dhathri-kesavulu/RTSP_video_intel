"""
Day 4 - ONVIF-style discovery/connection stub.

Full ONVIF device negotiation requires a real ONVIF-compliant camera to
test against, which a plain USB webcam pushed through MediaMTX is not.
This script demonstrates the actual ONVIF connection flow using the
onvif-zeep library — device info retrieval, media profile listing, and
stream URI negotiation — structured so it can be pointed at a real
ONVIF camera's IP address later without changing the logic.

Usage:
    python3 onvif_discovery.py --host <camera_ip> --port 80 --user admin --password admin
"""

import argparse
import sys

from onvif import ONVIFCamera


def discover_device(host: str, port: int, user: str, password: str) -> None:
    """
    Connects to an ONVIF-compliant camera and prints device info,
    available media profiles, and each profile's RTSP stream URI.
    """
    try:
        camera = ONVIFCamera(host, port, user, password)

        device_service = camera.create_devicemgmt_service()
        info = device_service.GetDeviceInformation()

        print("[OK] Connected to ONVIF device:")
        print(f"  Manufacturer : {info.Manufacturer}")
        print(f"  Model        : {info.Model}")
        print(f"  Firmware     : {info.FirmwareVersion}")
        print(f"  Serial       : {info.SerialNumber}")

        media_service = camera.create_media_service()
        profiles = media_service.GetProfiles()

        print(f"\n[OK] Found {len(profiles)} media profile(s):")
        for profile in profiles:
            print(f"  - {profile.Name} ({profile.token})")

            stream_setup = {
                "Stream": "RTP-Unicast",
                "Transport": {"Protocol": "RTSP"},
            }
            uri = media_service.GetStreamUri(
                {"StreamSetup": stream_setup, "ProfileToken": profile.token}
            )
            print(f"    Stream URI: {uri.Uri}")

    except Exception as exc:  # noqa: BLE001 - want to surface any ONVIF/network error clearly
        print(f"[ERROR] Could not complete ONVIF discovery: {exc}")
        print(
            "\nNote: this requires a real ONVIF-compliant camera on the "
            "network. A plain USB webcam does not speak ONVIF, so this "
            "script can't be tested end-to-end without one — document "
            "that clearly in the README rather than treating it as broken."
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal ONVIF discovery/connection stub."
    )
    parser.add_argument("--host", required=True, help="Camera IP address")
    parser.add_argument("--port", type=int, default=80, help="ONVIF service port (default: 80)")
    parser.add_argument("--user", required=True, help="ONVIF username")
    parser.add_argument("--password", required=True, help="ONVIF password")

    args = parser.parse_args()
    discover_device(args.host, args.port, args.user, args.password)


if __name__ == "__main__":
    main()
