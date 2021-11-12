import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from met_explore.views import single_cmpds_df
from met_explore.compound_selection import CompoundSelector
from met_explore.models import Analysis, Peak, Annotation
from met_explore.multi_omics import MultiOmics
from met_explore.compound_selection import get_cmpid_from_chebi

class Outliers(object):
    """
    This is a class to calculate and work with outliers in the metabolomics data - these outliers are metabolites within a set
    that are higher or lower than the other members in the set.
    """

    def __init__(self, analysis_id, column_set, k, run_std=False, isID=True):
        """

        :param analysis_id: The ID of the analysis
        :param column_set: All of the samples to be compared across the set, added as a list
        :param k: This parameter is used for IQR (1.5 = outlier, 3 = extreme outlier) or No of STD away from the means
        :param run_std: If True run standard deviation, otherwise run IQR
        :param isID: If True working with identified metabolites, if false working with all metabolites.
        """

        analysis = Analysis.objects.get(id=analysis_id)
        peaks = Peak.objects.all()
        cmpd_selector = CompoundSelector()
        self.isID = isID

        if isID:
            self.df = single_cmpds_df
        else:
            self.df = cmpd_selector.get_group_df(analysis, peaks)

        self.column_set = column_set
        self.run_std = run_std
        self.k = k
        self.peak_met_dict = pd.Series(single_cmpds_df.Metabolite.values, index=single_cmpds_df.index).to_dict()
        self.outlier_df = self.add_outliers_df()

    def get_prepared_df(self):

        select_df = self.df[self.column_set].copy()
        select_df = select_df.fillna(1000)  # Set the NA number to a minimum value
        select_df = np.log2(select_df)

        return select_df

    def add_outliers_df(self):

        if self.run_std:
            set_low_high_df = self.get_std_outlier_ranges()
        else: # Run IQR
            set_low_high_df = self.get_IQR_ranges()

        outlier_df = self._collect_mark_outliers(set_low_high_df)

        return outlier_df


    def get_std_outlier_ranges(self):
        """
        :param Nstds: Number of standard deviations away from the mean that should be set as an outlier
        :return: df with high and low ranges determined by std and mean
        """
        select_df = self.get_prepared_df()

        working_df = select_df.copy()

        working_df['Mean'] = select_df.mean(axis=1)
        working_df['STD'] = select_df.std(axis=1)
        select_df['lower_range'] = working_df['Mean'] - self.k * working_df['STD']
        select_df['upper_range'] = working_df['Mean'] + self.k * working_df['STD']

        return select_df

    def get_IQR_ranges(self):
        """
        df: the dataframe for which each row will have upper and lower ranges calculated
        k: k=1.5 gives outliers, whereas k=3 gives extreme outliers
        """
        select_df = self.get_prepared_df()

        Q3 = select_df.quantile(0.75, axis=1)
        Q1 = select_df.quantile(0.25, axis=1)
        IQR = Q3 - Q1
        lower_range = Q1 - self.k * IQR
        upper_range = Q3 + self.k * IQR
        select_df['lower_range'] = lower_range
        select_df["upper_range"] = upper_range

        return select_df

    def _collect_mark_outliers(self, id_ints_df):
        """

        :param id_ints_df: A df with lower and upper_range columns a
        :return: A df with values > upper ranges or < lower ranges replaced by 'High' or 'Low'
        """

        analysis_df = id_ints_df.astype('object').copy()
        for ix, row in id_ints_df.iterrows():

            high_indices = [i for i, v in enumerate(row) if v > row.upper_range]
            low_indices = [i for i, v in enumerate(row) if v < row.lower_range]
            if high_indices:
                for hi in high_indices:
                    analysis_df.loc[ix, analysis_df.columns[hi]] = "High"
            if low_indices:
                for li in low_indices:
                    analysis_df.loc[ix, analysis_df.columns[li]] = "Low"
        analysis_df = analysis_df.drop(columns=['lower_range', 'upper_range'])
        return analysis_df

    def get_hl_ix_dict(self, df):

        high_low_dict = {}
        for col in df.columns:
            hl_col = {}
            hl_col["High"] = df.index[df[col] == "High"].tolist()
            hl_col["Low"] = df.index[df[col] == "Low"].tolist()

            high_low_dict[col] = hl_col

        return high_low_dict

    def get_hl_count_dict(self):

        high_low_dict = {}
        for col in self.outlier_df.columns:
            hl_col = {}
            hl_col["NHigh"] = len(self.outlier_df.index[self.outlier_df[col] == "High"].tolist())
            hl_col["NLow"] = len(self.outlier_df.index[self.outlier_df[col] == "Low"].tolist())

            high_low_dict[col] = hl_col

        return high_low_dict

    def get_gene_high_low_dict(self, hl_ix_dict):
        """
        Given a dictionary of ix get back a list of names of metabolites that have high or low
        intensities
        """
        gene_high_low_dict = {}
        for gene, dct in hl_ix_dict.items():
            level_dict = {}
            for level, ix in dct.items():
                peak_list = [self.peak_met_dict[x] for x in ix]
                level_dict[level] = peak_list
            gene_high_low_dict[gene] = level_dict

        return gene_high_low_dict

    def get_hl_count_df(self):
        """
        method to take in a peak intensity df, a list of mutant names (group) and k (the IQR parameter)
        returns a DF listing mutants and the number of high and low intensity peaks.
        """
        peaks_count = self.get_hl_count_dict()
        count_df = pd.DataFrame(peaks_count)

        return count_df

    def get_high_low_df(self, peak_list=None):
        """
        This method takes an outlier df and returns a dictionary of High/Low values (isid=None)
        for the peak Ids or the identified metabolites (isid=True)
        """
        print (peak_list)
        if peak_list:
            outlier_df = self.outlier_df.loc[peak_list]
        else:
            outlier_df = self.outlier_df

        if self.isID:
            peaks_ix = self.get_hl_ix_dict(outlier_df)
            gene_high_low_dict = self.get_gene_high_low_dict(peaks_ix)
            high_low_df = pd.DataFrame.from_dict(gene_high_low_dict)
        else:
            peaks_ix = self.get_hl_ix_dict(outlier_df)
            high_low_df = pd.DataFrame.from_dict(peaks_ix)

        return high_low_df

    def write_identified_metabolites(self, fname):
        """

        :param fname: Filename to be written to
        :param k: no of stds or IQR k value
        :return: Write csv with sample: HIGH metabolites: LOW metabolites
        """
        set_high_low = self.get_high_low_df()
        set_high_low.transpose().to_csv("./data/high_low_mets/"+fname + '.csv')

    def get_all_peaks_boxplot(self, gene_name, sample_name):
        """
        This method looks for all the metabolites that should be associated with a gene and returns a box plot for all of
        the metabolites that are outliers in the data. Those that are not outliers are not returned.
        """
        omics_dict = self.get_omics_cmpd_dict(gene_name)
        cmpd_peaks = self.get_cmpd_peaks(omics_dict)
        for cmpd, peaks in cmpd_peaks.items():
            self.get_related_boxplot(cmpd, sample_name, omics_dict, cmpd_peaks)

    def get_cmpd_peaks(self, omics_dict):

        cmpd_peaks = {}
        for cmpd_id, cmpd in omics_dict.items():
            peak_conf = {}
            annots = Annotation.objects.filter(compound_id=cmpd_id)
            for a in annots:
                peak_conf[a.peak_id] = a.confidence

            peak_list = [peak for peak, conf in peak_conf.items() if conf > 0]
            if not peak_list:
                peak_list = [peak for peak, conf in peak_conf.items() if conf == 0]

            cmpd_peaks[cmpd_id] = peak_list

        return cmpd_peaks


    def get_omics_cmpd_dict(self, gene_name):

        analysis = Analysis.objects.get(id=1)
        mo = MultiOmics(analysis)
        fbgn = mo.get_fbgn_codes([gene_name])

        omics_data_df = mo.get_single_entity_relation(fbgn)
        omics_data_df.reset_index(inplace=True)
        omics_dict = {}

        compounds = omics_data_df[omics_data_df.data_type == 'compounds']

        for ix, row in compounds.iterrows():
            cmpd_id = get_cmpid_from_chebi(row.entity_id)
            if cmpd_id is not None:
                omics_dict[cmpd_id] = row.display_name
        return omics_dict



    def get_boxplot(self, sample_name, savefig=True):
        """

        :param sample_name: The sample that you want to look at all the outliers for identified metabolites
        :param savefig: Saves a PDF of the boxplot
        :return:
        """
        met_df = single_cmpds_df.set_index("Metabolite")
        met_df = met_df[self.column_set]

        hl_df = self.get_high_low_df()

        metabolite_names = hl_df[sample_name].High + hl_df[sample_name].Low
        met_df = met_df.fillna(1000)
        met_df = np.log2(met_df)

        select_df = met_df.loc[metabolite_names]
        columns = list(select_df.index)
        fig_width = len(columns)
        n = select_df[sample_name].values

        boxplot = select_df.T.boxplot(figsize=(fig_width, 8), rot=90)

        # Add the label MT at the intenisty position for each metabolite for the sample being analysed.
        for i in range(0, len(columns)):
            boxplot.annotate(
                'MT',
                xy=(i + 1.1, n[i]))  # put text at the RHS of the x point (+0.1)

        plt.xlabel('Metabolites', fontsize=14)
        plt.ylabel('Log2 Intensity', fontsize=14)
        plt.title(sample_name + ' (MT)', fontsize=14)

        plt.gcf().subplots_adjust(bottom=0.15, left=0.1, right=0.11)
        plt.tight_layout()
        if savefig:
            filename = sample_name + 'boxplot.pdf'
            plt.savefig("./data/boxplots/"+filename)

    def get_related_boxplot(self, cmpd, sample_name, omics_dict, cmpd_peaks):
        """
        A method to show the box plot of all the peaks that are outliers
        for a particular compound within a sample.

        :param cmpd: Pass the ID of the cmpd to be examined
        :param sample_name: Name of the samples e.g a particular mutant or tissue
        :param omics_dict: The compounds related to the sample of interest (Id:Name)
        :param cmpd_peaks: Cmpd_id: Related_peaks
        :return: Plots the boxplot
        """
        cmpd_name = omics_dict[cmpd]
        peak_list = cmpd_peaks[cmpd]
        hl_df = self.get_high_low_df(peak_list)
        hl_peaks = hl_df[sample_name].High + hl_df[sample_name].Low
        if hl_peaks:
            met_df = self.df.loc[hl_peaks].copy()
            met_df = met_df.fillna(1000)
            met_df = np.log2(met_df)

            select_df = met_df
            columns = list(select_df.index)
            if len(columns) < 2:
                fig_width = 2
            else:
                fig_width = len(columns)

            n = select_df[sample_name].values
            boxplot = select_df.T.boxplot(figsize=(fig_width, 8), rot=90)

            # Add the label MT at the intenisty position for each metabolite for the sample being analysed.
            for i in range(0, len(columns)):
                boxplot.annotate(
                    'MT',
                    xy=(i + 1.1, n[i]))  # put text at the RHS of the x point (+0.1)
            plt.xlabel(cmpd_name, fontsize=14)
            plt.ylabel('Log2 Intensity', fontsize=14)
            plt.title(sample_name + ' (MT)', fontsize=14)

            plt.gcf().subplots_adjust(bottom=0.15, left=0.1, right=0.11)
            plt.tight_layout()
            plt.show()
        else:
            print("There are no outliers for %s for sample %s " % (cmpd_name, sample_name))

