#!/usr/bin/env python3
"""Extract specific USRP FPGA images from the downloaded uhd-images package.

This script looks for `uhd-images*.deb` inside the `debFiles` directory created
by `gather_debs.py`. The X310 and B210 images are extracted into a directory
named `fpga_images` next to this script so the installer can load them without
network access.
"""

import argparse
import subprocess
import tempfile
from pathlib import Path
import shutil
import fnmatch


def extract_images(deb_path: Path, dest_dir: Path) -> None:
    """Extract the X310 and B210 FPGA images from a .deb package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["dpkg-deb", "-x", str(deb_path), tmpdir], check=True)
        tmp_path = Path(tmpdir)

        patterns = {
            "usrp_x310_fpga_*": "usrp_x310_fpga_XG.bit",
            "usrp_b210_fpga.*": "usrp_b210_fpga.bin",
            "usrp_b200_fpga.*": "usrp_b210_fpga.bin",
        }

        for pattern, output_name in patterns.items():
            for file in tmp_path.rglob(pattern):
                shutil.copy(file, dest_dir / output_name)
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract FPGA images from uhd-images package")
    parser.add_argument(
        "--deb-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "debFiles",
        help="Directory containing downloaded .deb packages",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "fpga_images",
        help="Directory to place the extracted FPGA images",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    deb_files = list(args.deb_dir.glob("uhd-images*.deb"))
    if not deb_files:
        print(f"No uhd-images package found in {args.deb_dir}")
        return

    for deb in deb_files:
        extract_images(deb, args.out_dir)
        print(f"Extracted images from {deb}")


if __name__ == "__main__":
    main()
