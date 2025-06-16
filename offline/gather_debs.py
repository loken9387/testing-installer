import argparse
import csv
import subprocess
from pathlib import Path

from typing import List


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


def download_package(package: str, dest: Path) -> List[str]:
    """Download *package* and return the list of newly created .deb files in
    the order they were retrieved."""
    before = {p.name: p.stat().st_mtime for p in dest.glob('*.deb')}


    if package.startswith('./google-chrome-stable_current_amd64.deb'):
        url = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
        output = dest / 'google-chrome-stable_current_amd64.deb'
        subprocess.run(['wget', '-O', str(output), url], check=True)
    else:
        # Use apt-get's install command in download-only mode so that
        # all dependencies of the package are fetched as well.
        subprocess.run(
            [
                'apt-get',
                'install',
                '--download-only',
                '--yes',
                '-o', f'Dir::Cache={dest}',
                '-o', f'Dir::Cache::archives={dest}',
                package,
            ],
            check=True,
        )

    after = {p.name: p.stat().st_mtime for p in dest.glob('*.deb')}
    new = [(name, after[name]) for name in after.keys() - before.keys()]
    new.sort(key=lambda t: t[1])
    return [name for name, _ in new]



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
    seen = {}
    for package in packages:
        try:
            new_files = download_package(package, download_dir)
            for fname in new_files:
                seen[fname] = (download_dir / fname).stat().st_mtime
        except subprocess.CalledProcessError as exc:
            print(f"Failed to download {package}: {exc}")


    order_path = download_dir / 'package_order.txt'
    with order_path.open('w') as order_file:
        for name, _ in sorted(seen.items(), key=lambda item: item[1]):
            order_file.write(name + '\n')

    if args.tar:
        tar_path = script_dir / 'debFiles.tar.gz'
        create_tarball(download_dir, tar_path)


if __name__ == '__main__':
    main()
