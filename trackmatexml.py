"""
TrackmateXML
For reading .xml files generated by ImageJ TrackMate https://imagej.net/TrackMate
v1.0
(c) R.Harkes - NKI

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path


class TrackmateXML:
    """
    Trackmate-xml is a class around trackmate xml files to simplify some typical operations on the files, while still
    maintaining access to the raw data.
    """
    class_version = 1.0

    def __init__(self, filename):
        if isinstance(filename, str):
            self.pth = Path(filename)
        elif isinstace(filename, Path):
            self.pth = filename
        else:
            raise ValueError('not a valid filename')

        if self.pth.suffix == '.h5':
            store = pd.HDFStore(self.pth)
            self.spots = store.spots
            self.tracks = store.tracks
            self.filteredtracks = store.filtered_tracks
            other_info = store.other_info
            self.version = other_info.version[0]
            store.close()
        elif self.pth.suffix == '.xml':
            etree = ET.parse(self.pth)
            root = etree.getroot()
            if not root.tag == 'TrackMate':
                raise ValueError('Not a TrackmateXML')
            self.version = root.attrib['version']
            self.spots = self.__loadspots(root)
            self.tracks = self.__loadtracks(root)
            self.filteredtracks = self.__loadfilteredtracks(root)
        else:
            raise ValueError('{0} is not avalid file suffix'.format(self.pth.suffix))

    def save(self, filename, create_new=True):
        """
        Saves the spots, tracks and filteredtracks to an HDFStore
        """
        if isinstance(filename, str):
            pth = Path(filename)
        elif isinstace(filename, Path):
            pth = filename
        else:
            raise ValueError('not a valid filename')
        if pth.exists() & create_new:
            pth.unlink()
        store = pd.HDFStore(pth)
        store['spots'] = self.spots
        store['tracks'] = self.tracks
        store['filtered_tracks'] = self.filteredtracks
        other_info = {'version': self.version, 'class_version': TrackmateXML.class_version}
        store['other_info'] = pd.DataFrame(other_info, index=[0])
        store.close()

    @staticmethod
    def __loadfilteredtracks(root):
        """
        Loads all filtered tracks from xml
        :param root: root of xml
        :return: filtered tracks
        """
        filtered_tracks = []
        for track in root.iter("TrackID"):
            track_values = track.attrib
            track_values['TRACK_ID'] = int(track_values.pop('TRACK_ID'))
            filtered_tracks.append(track_values)
        ftracks = pd.DataFrame(filtered_tracks)
        return ftracks

    @staticmethod
    def __loadtracks(root):
        """
        load all tracks in the .xml file
        :param root: root of .xml file
        :return: tracks as pandas dataframe
        """
        all_tracks = []
        for track in root.iter("Track"):
            curr_track = int(track.attrib["TRACK_ID"])
            all_edges = []
            for edge in track:
                edge_values = edge.attrib
                edge_values['SPOT_SOURCE_ID'] = int(edge_values.pop('SPOT_SOURCE_ID'))
                edge_values['SPOT_TARGET_ID'] = int(edge_values.pop('SPOT_TARGET_ID'))
                edge_values['TrackID'] = curr_track
                all_edges.append(edge_values)
            all_tracks.append(pd.DataFrame(all_edges))
        tracks = pd.concat(all_tracks)
        return tracks

    @staticmethod
    def __loadspots(root):
        """
        Loads all spots in the xml file
        :return: spots as pandas dataframe
        """
        # load all spots
        all_frames = []
        for spots_in_frame in root.iter("SpotsInFrame"):
            curr_frame = spots_in_frame.attrib["frame"]
            # go over all spots in the frame
            all_spots = []
            for spot in spots_in_frame:
                spot_values = spot.attrib
                spot_values.pop('name')  # not needed
                spot_values['Frame'] = curr_frame
                spot_values['ID'] = int(spot_values.pop('ID'))  # we want ID to be integer, so we can index later
                all_spots.append(spot_values)
            all_frames.append(pd.DataFrame(all_spots))

        spots = pd.concat(all_frames)
        spots.set_index('ID', inplace=True, verify_integrity=True)
        spots = spots.astype('float')
        return spots

    def trace_track(self, track_id, verbose=False):
        """
        Traces a track over all spots.
        :param verbose: report if a split is found
        :param track_id:
        """
        assert isinstance(track_id, int)
        # Tracks consist of edges. The edges are not sorted
        current_track = self.tracks[self.tracks['TrackID'] == track_id]
        if current_track.empty:
            raise ValueError('track {0} not found'.format(track_id))
        track_splits = []
        source_spots = self.spots.loc[current_track['SPOT_SOURCE_ID'].values].reset_index()
        target_spots = self.spots.loc[current_track['SPOT_TARGET_ID'].values].reset_index()
        currentindex = source_spots['Frame'].idxmin()
        whole_track = [source_spots.loc[currentindex], target_spots.loc[currentindex]]
        # can we continue from the target to a new source?
        current_id = target_spots['ID'].loc[currentindex]
        currentindex = source_spots.index[source_spots['ID'] == current_id].tolist()
        while len(currentindex) > 0:
            if len(currentindex) > 1:
                currentindex = currentindex[0]
                fr = target_spots['Frame'].loc[currentindex]
                if verbose:
                    print("Got a split at frame {0} Will continue on branch 0".format(int(fr)))
                    # but so far we do nothing with this knowledge
                track_splits.append(fr)
            else:
                currentindex = currentindex[0]
            whole_track.append(target_spots.loc[currentindex])
            current_id = target_spots['ID'].loc[currentindex]
            currentindex = source_spots.index[source_spots['ID'] == current_id].tolist()
        whole_track = pd.concat(whole_track, axis=1).T.reset_index(drop=True)
        return whole_track, track_splits


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fn = 'Control_Fused-Bckgrnd.xml'
    txml = TrackmateXML(fn)
    print("Version of trackmateXML file is {0}".format(txml.version))
    txml.save('Control_Fused-Bckgrnd.h5')
    track_nr = 1
    my_track, splits = txml.trace_track(track_nr, verbose=True)
    plt.plot(my_track['Frame'], my_track['MEAN_INTENSITY01'], 'g',
             my_track['Frame'], my_track['MEAN_INTENSITY02'], 'r')
    plt.ylabel('Intensity (a.u.)')
    plt.xlabel('Time (frames)')
    plt.title("Track {0}".format(track_nr))
    for xc in splits:
        plt.axvline(x=xc, color='k')
    plt.show()
