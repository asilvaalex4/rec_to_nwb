from rec_to_nwb.processing.tools.beartype.beartype import beartype
from rec_to_nwb.processing.tools.filter_probe_by_type import filter_probe_by_type


class FlElectrodeExtensionFactory:

    @classmethod
    @beartype
    def create_rel(cls, probes_metadata: list, electrode_groups_metadata: list) -> dict:

        rel_x, rel_y, rel_z = [], [], []
        for electrode_group_metadata in electrode_groups_metadata:
            probe_metadata = filter_probe_by_type(probes_metadata, electrode_group_metadata['device_type'])

            for shank in probe_metadata['shanks']:
                for electrode in shank['electrodes']:
                    rel_x.append(float(electrode['rel_x']))
                    rel_y.append(float(electrode['rel_y']))
                    rel_z.append(float(electrode['rel_z']))
        return {'rel_x': rel_x, 'rel_y': rel_y, 'rel_z': rel_z}

    @classmethod
    @beartype
    def create_ntrode_id(cls, ntrode_metadata: list) -> list:
        ntrode_id = []
        [ntrode_id.extend([ntrode['ntrode_id']] * len(ntrode['map'])) for ntrode in ntrode_metadata]
        return ntrode_id

    @classmethod
    @beartype
    def create_channel_id(cls, ntrode_metadata: list) -> list:
        channel_id = []
        for ntrode in ntrode_metadata:
            [channel_id.append(map_index) for map_index in ntrode['map']]
        return channel_id

    @classmethod
    @beartype
    def create_bad_channels(cls, ntrode_metadata: list) -> list:
        bad_channels = []
        for ntrode in ntrode_metadata:
            bad_channels.extend(
                [bool(counter in ntrode['bad_channels']) for counter, _ in enumerate(ntrode['map'])]
            )
        return bad_channels

    @classmethod
    @beartype
    def create_hw_chan(cls, spike_n_trodes: list) -> list:
        hw_chan = []
        for spike_n_trode in spike_n_trodes:
            [hw_chan.append(int(spike_channel.hw_chan)) for spike_channel in spike_n_trode.spike_channels]
        return hw_chan

    @classmethod
    @beartype
    def create_probe_shank(cls, probes_metadata: list, electrode_groups_metadata: list):
        probe_shank = []
        for electrode_group_metadata in electrode_groups_metadata:
            probe_metadata = filter_probe_by_type(probes_metadata, electrode_group_metadata['device_type'])
            [probe_shank.extend([shank['shank_id']] * len(shank['electrodes'])) for shank in probe_metadata['shanks']]
        return probe_shank

    @classmethod
    def create_probe_electrode(cls, probes_metadata: list, electrode_groups_metadata: list):
        probe_electrode = []
        for electrode_group_metadata in electrode_groups_metadata:
            probe_metadata = filter_probe_by_type(probes_metadata, electrode_group_metadata['device_type'])
            for shank in probe_metadata['shanks']:
                [probe_electrode.append(electrode['id']) for electrode in shank['electrodes']]
        return probe_electrode

    @classmethod
    def create_ref_elect_id(cls, spike_n_trodes: list, ntrode_metadata: dict):
        # create a list of ntrode_ids, channels, and their indices
        ntrode_elect_id = dict()
        elect_id = 0
        for ntrode in ntrode_metadata:
            ntrode_id = ntrode['ntrode_id']
            ntrode_elect_id[ntrode_id] = dict()
            for chan in ntrode["map"]:
                # adjust for 1 based channel numbers in rec file header: ntrode["map"] is 0 based, so we have to add 1 to the zero based number to get the  index
                # that corresponds to spike_n_trode.ref_chan below
                ntrode_elect_id[ntrode_id][int(chan)+1] = elect_id
                elect_id+=1

        ref_elect_id = []
        for spike_n_trode in spike_n_trodes:
            if spike_n_trode.ref_n_trode_id:
                for ntrode in ntrode_metadata:
                    if int(ntrode["ntrode_id"]) == int(spike_n_trode.ref_n_trode_id):
                        ref_elect_id.extend(
                            [ntrode_elect_id[spike_n_trode.ref_n_trode_id][int(spike_n_trode.ref_chan)]]
                            * len(spike_n_trode.spike_channels)
                        )
            else:
                ref_elect_id.extend([-1] * len(spike_n_trode.spike_channels))
        return ref_elect_id


