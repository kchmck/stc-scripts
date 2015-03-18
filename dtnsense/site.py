import codecs
import configparser
import hashlib
import hmac

class Format:
    __slots__ = ["id"]

    def __init__(self, id):
        assert id <= 9999

        self.id = id

    def __str__(self):
        return "{:04}".format(self.id)

class Location:
    __slots__ = ["name", "num"]

    def __init__(self, name, num):
        assert len(name) <= 3
        assert num <= 9999

        self.name = name
        self.num = num

    def __str__(self):
        return "{:>3}{:>4}".format(self.name, "{:03}".format(self.num))

class Key:
    __slots__ = ["id", "bytes"]

    def __init__(self, id, bytes):
        assert id <= 999

        self.id = id
        self.bytes = bytes

    def __str__(self):
        return "{:03}".format(self.id)

class Config:
    __slots__ = ["loc", "key", "fmt"]

    def __init__(self, path):
        parser = configparser.ConfigParser()
        parser.read(path)

        self.loc = Location(parser["location"]["name"],
                            int(parser["location"]["site"]))
        self.key = Key(int(parser["signing"]["key_id"]),
                       codecs.decode(parser["signing"]["key"], "hex_codec"))
        self.fmt = Format(int(parser["record"]["format_id"]))

class Record:
    __slots__ = ["cfg", "date", "temp", "ph", "cond", "tz"]

    def __init__(self, cfg, date, temp, ph, cond, tz="+0000"):
        assert -999.995 < temp < 999.995
        assert 0 < ph < 99.9995
        assert 0 < cond < 999999.995

        self.cfg = cfg
        self.date = date
        self.temp = temp
        self.ph = ph
        self.cond = cond
        self.tz = tz

    def format_temp(self, temp):
        # This has to be done this way because python's format strings include
        # the +/- in the width of the field, where in the spec it says only the
        # number should be padded.
        return "{}{:6.2f}".format("-" if temp < 0 else "+", abs(temp))

    def __str__(self):
        return "{}{}{}{}{}{}{:6.3f}{:9.2f}".format(
            self.cfg.loc,
            self.cfg.key,
            self.cfg.fmt,
            self.date.strftime("%Y-%m-%d %H:%M:%S"),
            self.tz,
            self.format_temp(self.temp),
            self.ph,
            self.cond
        )

class SignedRecord:
    __slots__ = ["record", "sig"]

    def __init__(self, cfg, record):
        self.record = str(record)
        self.sig = hmac.new(cfg.key.bytes,
            self.record.encode("ascii"), hashlib.sha256)

    def __str__(self):
        return "".join((self.record, self.sig.hexdigest()))

if __name__ == "__main__":
    # Here's the example from box.
    import datetime

    class Config:
        def __init__(self):
            self.loc = Location("HF", 95)
            self.fmt = Format(1)
            self.key = Key(1, b"\xa8\x89z3!\xce\xd5~\x84W\xaf\xb7")

    cfg = Config()
    record = Record(cfg, datetime.datetime(2014,10,27,13,0,0), 20.20, 4.123, 359.0, "-0400")
    signed = SignedRecord(cfg, record)

    print(signed)
    assert str(signed) == " HF 09500100012014-10-27 13:00:00-0400+ 20.20 4.123   359.00aacb89f70d1fa3d38e7faeac711b105678eeba4edc2e7903e6454b6d06a457e8"
