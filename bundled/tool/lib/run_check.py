import subprocess


def run_djangoly_on_file(file_path: str) -> str:
    try:
        result = subprocess.run(
            ['djangoly', 'check', file_path],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)
