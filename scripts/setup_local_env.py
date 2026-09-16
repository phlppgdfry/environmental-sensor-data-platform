"""Create local demo credentials once; never overwrite an existing .env."""
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    password = secrets.token_hex(24)
    values = {
        "POSTGRES_PASSWORD": password,
        "DATABASE_URL": f"postgresql+psycopg2://sensor_platform:{password}@localhost:5432/sensor_platform",
    }
    lines = []
    for line in (ROOT / ".env.example").read_text().splitlines():
        key, separator, _ = line.partition("=")
        lines.append(f"{key}={values[key]}" if separator and key in values else line)
    try:
        fd = os.open(ROOT / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SystemExit(".env already exists; keep it or update it manually.") from None
    with os.fdopen(fd, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("Created .env with unique local credentials. Existing databases are unchanged.")


if __name__ == "__main__":
    main()
