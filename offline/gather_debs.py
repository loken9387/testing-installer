import argparse
import csv
import subprocess
from pathlib import Path


def read_packages(csv_path: Path) -> list[str]:
    packages = []
    with csv_path.open() as f:
        for row in csv.reader(f):
            if not row:
                continue
            pkg = row[0].strip()
            if pkg and not pkg.startswith('#'):
                packages.append(pkg)
    return packages


def download_package(package: str, dest: Path):
    if package.startswith('./google-chrome-stable_current_amd64.deb'):
        url = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
        output = dest / 'google-chrome-stable_current_amd64.deb'
        subprocess.run(['wget', '-O', str(output), url], check=True)
    else:
        # Clean old .deb files for this package (optional)
        for f in dest.glob(f"{package}_*.deb"):
            f.unlink()

        subprocess.run(
            [
                'apt-get', 'install', '--download-only', '--yes',
                '--reinstall',  # Ensures action even if installed
                '-o', f'Dir::Cache={dest}',
                '-o', f'Dir::Cache::archives={dest}',
                package,
            ],
            check=True,
        )


def create_tarball(src_dir: Path, tar_path: Path):
    subprocess.run(['tar', '-czvf', str(tar_path), '-C', str(src_dir), '.'], check=True)


def main():
    parser = argparse.ArgumentParser(description='Gather .deb files for offline install')
    parser.add_argument('--tar', action='store_true', help='Create debFiles.tar.gz archive')
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    packages_file = script_dir.parent / 'packages.csv'
    download_dir = script_dir / 'debFiles'
    download_dir.mkdir(parents=True, exist_ok=True)

    packages = read_packages(packages_file)
    for package in packages:
        try:
            download_package(package, download_dir)
        except subprocess.CalledProcessError as exc:
            print(f"Failed to download {package}: {exc}")

    if args.tar:
        tar_path = script_dir / 'debFiles.tar.gz'
        create_tarball(download_dir, tar_path)


if __name__ == '__main__':
    main()
