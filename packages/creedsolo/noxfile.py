import argparse
import shutil
from pathlib import Path

import nox

nox.needs_version = ">=2026.2"


@nox.session
def cibuild_prepare(session: nox.Session) -> None:
    """Clean creedsolo's CMake output folder if it exists"""

    current_file = Path(__file__).resolve()
    project_path = current_file.parent

    build_path = project_path / "build"

    if session.posargs:
        sub_parser = argparse.ArgumentParser(
            prog="Nox CIBuildWheel environment cleaner"
        )
        sub_parser.add_argument("-o", "--build-path", type=Path)
        sub_namespace = sub_parser.parse_args(session.posargs)

        try:
            if sub_namespace.build_path:
                build_path = Path(sub_namespace.build_path).resolve(strict=True)
        except (FileNotFoundError, RuntimeError, OSError) as exc:
            session.error(
                f"Encountered an error when trying to resolve build path to clean: {exc}"
            )

        try:
            _ = build_path.relative_to(project_path)
        except ValueError:
            session.error(
                "The provided path must point to subdirectories under project root only."
            )

        if build_path == project_path:
            session.error(
                "The provided path must point to subdirectories under project root only."
            )

        if not build_path.is_dir():
            session.error(
                "The provided path must point to subdirectories under project root only."
            )

    session.log(f"Removing previous build path {build_path}")

    if build_path.exists():
        shutil.rmtree(build_path)