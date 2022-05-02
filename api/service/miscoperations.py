import hashlib


class MiscOperations:
    @staticmethod
    def get_partition_value(value: str) -> float:
        b = value.encode("ascii")
        h = hashlib.md5(b).hexdigest()
        local_hash = h.upper().replace("-", "")
        num_string = local_hash[0:6]
        num = int(num_string, 16)
        pct = num / 0xFFFFFF

        return pct
