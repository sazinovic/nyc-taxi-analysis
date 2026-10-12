"""Execute every analysis notebook from a fresh kernel and save checked outputs."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = args.notebooks or sorted((root / "notebooks").glob("*.ipynb"))
    for path in paths:
        print(f"Executing {path.name}", flush=True)
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(root)}}).execute()
        nbformat.validate(notebook)
        nbformat.write(notebook, path)
        print(f"Saved {path.name}: clean-kernel execution passed", flush=True)


if __name__ == "__main__":
    main()
