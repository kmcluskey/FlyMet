from met_explore.serializers import *
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

# Give the sample CSV file to populate the samples.
# KMcL: Working but need to consider the filepath.

def populate_samples(sample_csv):

    sample_details = np.genfromtxt(sample_csv, delimiter=',', dtype=str)[2:]
    print ("sd_type", sample_details)
    for sample in sample_details:
        # sample = s.split()
        sample_serializer = SampleSerializer(
            data={"name": sample[0], "group": sample[1], "life_stage": sample[2], "tissue": sample[3],
                  "mutant": sample[4]})
        if sample_serializer.is_valid():
            db_sample = sample_serializer.save()
            print ("sample saved ", db_sample.name)
        else:
            print (sample_serializer.errors)


# This requires the input taken from the construct_peak_df method/
# It requires all secondary_ids to be unique and reports any errors (throw?)
# To get the list and dict back from the json.dumps just use json.loads

def populate_peaks(peak_df):
    peak_array = peak_df.values
    for peak in peak_array:
        print(peak)
        cmpd_id = json.dumps(peak[12])
        frank_annot = json.dumps(peak[13])

        peak_serializer = PeakSerializer(
            data={"psec_id": peak[1], "m_z": format(peak[2], '.9f'), "neutral_mass": format(peak[14], '.9f'),
                  "rt": peak[3], "polarity": peak[4],
                  "cmpd_name": peak[10], "cmpd_formula": peak[6], "cmpd_identifiers": cmpd_id, "identified": peak[8],
                  "frank_anno": frank_annot, "adduct": peak[7], "db": peak[11]})
        if peak_serializer.is_valid():
            db_peak = peak_serializer.save()
            print ("peak saved ", db_peak.psec_id)
        else:
            print (peak_serializer.errors)

#Takes a peak intensity DF and a pimp peak id / secondary id dictionary to populate the PeakSamples.
#The dictionary is passed in as the Peak model only stores the psec id and not the pid from PiMP.

def populate_peaksamples(intensity_df, pids_sids_dict):

    columns = list(intensity_df.columns)
    for col in columns:
        sample = Sample.objects.get(name=col)
        this_col = intensity_df[col]
        # Get the data for the SamplePeak
        for index, value in this_col.iteritems():
            sec_id = pids_sids_dict[index]
            intensity = value
            peak = Peak.objects.get(psec_id=sec_id)
            print ("we are adding the data for: ", sample, peak, "intensity of", intensity)

            # Populate the DB
            samplepeak_serializer = SamplePeakSerializer(
                data={"peak": peak.id, "sample": sample.id, "intensity": intensity})
            if samplepeak_serializer.is_valid():
                db_samplepeak = samplepeak_serializer.save()
                print ("peak saved ", db_samplepeak.peak)
            else:
                print (samplepeak_serializer.errors)




