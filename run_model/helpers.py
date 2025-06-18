import re
import zlib


def generate_id(params: str, metadata: dict) -> str:
    crc32 = f"{zlib.crc32(params.encode('utf-8')):x}"
    scenario_sanitized = re.sub("[^a-z0-9]+", "-", metadata["scenario"])
    # id needs to be of length 1-63, but the last 9 characters are a - and the hash
    return (f"{metadata['dataset']}-{scenario_sanitized}"[0:54] + "-" + crc32).lower()