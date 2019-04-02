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
# This has been refactored to populate Peak, Annotation and Compound models.


#This population script currently only takes a single peak DB (one peak for one ID) and each ID has a compound associated with it
#These compounds will have duplicate entries.

def populate_filtered_peaks_cmpds(peak_df):
    """

    :param peak_df: A dataframe of filtered peaks from the peak_selector based on adducts, identification, fragmentation
    -it also ony returns a single peak (single sec_id from PiMP)
    :return: Populates the peaks, compounds and annotations for the filtered peaks.
    """
    peak_array = peak_df.values

    # For each row of the DF grab the peak, compound and annotation that relates them.
    for peak in peak_array:

        confidence_level = 1 #The annotations from the peak DF have a confidence level of 1

        print("The row we are working on is", peak)

        # Populating the peak fron the row
        peak_serializer = PeakSerializer(
            data={"psec_id": peak[1], "m_z": format(peak[2], '.9f'), "neutral_mass": format(peak[14], '.9f'),
                  "rt": peak[3], "polarity": peak[4]})

        if peak_serializer.is_valid():
            db_peak = peak_serializer.save()
            logger.info("peak saved %s", db_peak.psec_id)
        else:
            logger.warning("peak errors %s", peak_serializer.errors)

        # Populating the compound from the row.
        cmpd_id = json.dumps(peak[12])

        store_cmpd, created = Compound.objects.get_or_create(cmpd_name = peak[10], cmpd_formula= peak[6],
                                                   cmpd_identifiers= cmpd_id)
        logger.info("A new compound %s was created %s", store_cmpd.cmpd_name, created)

        # Populating the Annotation to relate the peak to the annotation and vice-versa

        frank_annot = json.dumps(peak[13])
        store_peak = Peak.objects.get(psec_id=peak[1])

        annot_serializer = AnnotationSerializer(
            data={ "compound":store_cmpd.id, "peak":store_peak.id, "identified": peak[8],
               "frank_anno": frank_annot, "db": peak[11], "adduct": peak[7], "confidence": confidence_level})
        if annot_serializer.is_valid():
            db_annot = annot_serializer.save()
            logger.info("annotation saved for compound %s and peak %s", db_annot.compound.cmpd_name, db_annot.peak.psec_id)
        else:
            db_annot = None
            logger.warning("annot_errors with no annotation %s", annot_serializer.errors)

        # Set the preferred candidate annotation and a reason

        store_peak.preferred_annotation = db_annot
        store_peak.preferred_annotation_reason = "Auto generated as this is a high confidence annotation"



    logger.info("The filtered peaks, compounds and annotations have been populated")




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




