from pathlib import Path


def read_txt_file(filepath: str | Path) -> dict:
    result = {}
    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.strip()
            if not line:
                continue

            if ',' in line:
                sep = ','
            elif ';' in line:
                sep = ';'
            else:
                continue

            parts = line.split(sep, 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result[key] = value

    return result
