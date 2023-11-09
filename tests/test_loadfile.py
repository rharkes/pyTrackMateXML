import tomllib
from pathlib import Path
from trackmatexml import TrackmateXML
import pytest


@pytest.fixture
def datainfo():
    file = Path(
        Path.cwd(),
        "tests",
        "testdata",
        "datainfo.toml",
    )
    with open(file, "rb") as f:
        data = tomllib.load(f)
    return data


def testloadfile(datainfo):
    for key in datainfo:
        file = Path(Path.cwd(), "tests", "testdata", key + ".xml")
        tmxml = TrackmateXML()
        tmxml.loadfile(file)
        assert tmxml.version == datainfo[key]["version"]
        assert tmxml.timeunits == datainfo[key]["timeunits"]
        assert tmxml.spatialunits == datainfo[key]["spatialunits"]
        assert tmxml.spots.shape[0] == datainfo[key]["nspots"]
        assert len(tmxml.tracks) == datainfo[key]["ntracks"]
        assert tmxml.tracknames == datainfo[key]["tracknames"]


def testgettraces(datainfo):
    for key in datainfo:
        file = Path(Path.cwd(), "tests", "testdata", key + ".xml")
        tmxml = TrackmateXML()
        tmxml.loadfile(file)
        trackmeans = datainfo[key]["trackmeans"]
        for track in trackmeans:
            for spotproperty in trackmeans[track]:
                traces = tmxml.gettraces(track, spotproperty)
                for i in range(len(traces)):
                    assert traces[i].mean() == pytest.approx(
                        trackmeans[track][spotproperty][i], 0.001
                    )
