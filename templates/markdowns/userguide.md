{% load staticfiles %}

# Getting started

**Please Note**

*For space and portability reasons, PiMP relies on centroided single polarity data in the MzXML format. If you are unable to convert your data into MzXML, please look at the <a href="http://proteowizard.sourceforge.net/tools.shtml" target="_blank" title="Guide">msconvert tool guide</a>.*

*PiMP supports all latest web browser, however features are primarily developed using Google Chrome, we strongly advise users to use this web browser for optimal experience. Chrome can be downloaded <a href="https://www.google.com/chrome/" target="_blank" title="Chrome">here</a>.*

---

## Logging in to PiMP:

To log in to PiMP, go to: <a href="http://polyomics.mvls.gla.ac.uk/accounts/login/" target="_blank" title="PiMP">PiMP Login page</a>

Once there, please input your username and password.
If you have not been provided with a username and password, please contact the PiMP administrator. Once you hit enter, or click 'Submit', you should find yourself in your profile page. From here you can see some general information about your projects, collaborators and the amount of storage you have used.

<!-- ![Project Management Page][project_management] -->
<p class="centered">
<img src="{% static 'userguide/img/Project_Management.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

From here, you can click on 'My Projects' to create a new project and start your analysis.

<!-- ![My Projects Page][my_projects] -->
<p class="centered">
<img src="{% static 'userguide/img/My_Projects.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Prerequisites
-------------

To analyse your data, you first need:
1. Your data in MzXML format
2. Your experimental design

Once you have these things available, please click on ‘Create Project’.

<!-- ![Create Project][create_project] -->
<p class="centered">
<img src="{% static 'userguide/img/Create_Project_Button.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

## Create Project:

To create your project, first give it a title, then a description. The description is useful as it allows you to tag your projects so they are easily browsable. Then click 'Create project'.

<!-- ![Project Dialog][project_dialog] -->
<p class="centered">
<img src="{% static 'userguide/img/Create_project_dialog.png' %}" class="img-thumbnail" alt="Profile page" width="20%" style="float:none;margin:auto;">
</p>

---

## Project Administration:

In ‘Project Administration’, you can add users to your project (via the ‘add users’ button), edit the title of your project or change the description (via the ‘edit title’ and ‘edit’ buttons respectively.

<!-- ![Project Administration][project_administration] -->
<p class="centered">
<img src="{% static 'userguide/img/project_administration.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Once you have performed any desired administration in this page, enter setup files by clicking on the ‘Setup’ tab.

---

## Setup:

To start creating a metabolomics experiment, you can first provide a group of supporting data files. Note that files are not necessary for the analysis to run. These supporting files consist of blanks, standards files and pooled/QC files. The blanks and pooled/QCs must be in MzXML format and the standards files must be in CSV format using the default Polyomics standards mixes (click here for downloadable examples; <a href="http://polyomics.mvls.gla.ac.uk/static/userguide/stds1.csv" title="Standards 1">Standards 1</a>, <a href="http://polyomics.mvls.gla.ac.uk/static/userguide/stds2.csv" title="Standards 2">Standards 2</a>, <a href="http://polyomics.mvls.gla.ac.uk/static/userguide/stds3.csv" title="Standards 3">Standards 3</a>). MzXML files must be uploaded in pairs: both a positive ionization mode and negative ionization mode version of each file. The pair of files must have the same name. Once a pair is uploaded, this is denoted by + - symbols next to the filename.

<!-- ![Setup][calibration_samples] -->
<p class="centered">
<img src="{% static 'userguide/img/calibration_samples.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

To upload any of the files, click on the blue button with an up arrow in the Available Samples box. A new window will appear allowing you to drag and drop your files for upload.

---

## Upload File (calibration data):

Simply drag and drop the blanks and pooled/QC MzXML files and standards files in csv format into the box below, then click the green ‘start upload’ button.

<!-- ![Upload Files Dialog][upload_files] -->
<p class="centered">
<img src="{% static 'userguide/img/upload_files.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

MzXML files must be uploaded in pairs: both a positive ionization mode and negative ionization mode version of each file. The pair of files must have the same name. Once a pair is uploaded, this is denoted by + - symbols next to the filename.

Once your samples are uploaded, assign them to their appropriate categories (either standards, blank or QC).

<!-- ![Assign Setup[assign_calibration_samples] -->
<p class="centered">
<img src="{% static 'userguide/img/Assign_Calibration_samples.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

To assign your samples to groups, highlight the samples in that group and then click the '+' symbol next to the appropriate group title.

<!-- ![Assign to QC Group][assign_qc] -->
<p class="centered">
<img src="{% static 'userguide/img/assign_qc.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

You can use the 'search' box to free text filter the file list.

<!-- ![Search Calibrations][search_calib] -->
<p class="centered">
<img src="{% static 'userguide/img/search_calib.png' %}" class="img-thumbnail" alt="Profile page" width="40%" style="float:none;margin:auto;">
</p>

Once all of the files have been uploaded and assigned, click the ‘Sample Management’ tab.

---

## Sample Management:

To begin uploading files, click the blue ‘upload files’ button in the ‘Samples’ box.  Once your samples are uploaded, you can apply an experimental design by clicking on the ‘Create’ button.

---

> *Tips*

> * Use the peak discovery tool to seach for specific compounds or internal standards in your samples before starting the analysis. To access it, click on <img src="{% static 'userguide/img/peak_icon.png' %}" class="img-thumbnail" alt="Profile page" width="30px" style="float:none;margin:auto;">

---


## Experimental Design:

Currently, PiMP supports experiments defined by discrete categories. Thus experiments must be defined in terms of conditions: wild type, mutant, time 0, time 30, no drug, low dose, high dose, etc. You can have as many conditions as you like, although bear in mind that a large number of conditions in a single experiment are hard to visualize effectively – you might be better to create multiple experiments. Once you have defined your conditions, click ‘Next’.

<!-- ![Experiment Definition][experiment_definition] -->
<p class="centered">
<img src="{% static 'userguide/img/experiment_definition.png' %}" class="img-thumbnail" alt="Profile page" width="40%" style="float:none;margin:auto;">
</p>

---

## Assign Samples:

You can now drag and drop the files into the conditions you have specified. Once you have completed your assignment, click ‘Submit’, and click on the ‘Analysis’ tab.

## Analysis:
Once you have defined a project and set up the calibration and experimental samples, you can create a new analysis to be submitted to the server, you must click on the ‘+ Create’ button.

<!-- ![Analysis List][analysis_list] -->
<p class="centered">
<img src="{% static 'userguide/img/analysis_list.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

You may provide an experiment name, and define the comparisons to be made. A comparison is simply a statistical comparison between two experimental groups, e.g. wild type vs mutant, or time 90 vs time 0. You can create as many comparisons as you like: click ‘Add Comparison’ to add another to the list for this experiment. It is also possible to change the default parameters to XCMS and mzMatch, by clicking the Change Parameters tab. When you have created the comparisons that you are interested in, click ‘Save'.

<!-- ![Analysis Definition][analysis_definition] -->
<p class="centered">
<img src="{% static 'userguide/img/analysis_definition.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

 You are returned to the ‘Analysis’ tab. Your newly created analysis will be at the bottom of the list of current analyses. Simply click ‘Submit analysis’ to submit the analysis to the server. A lot of computational analysis is now performed on the data – please refer to [this paper](http://pubs.acs.org/doi/abs/10.1021/ac2000994) for a description of the analytical process. When the analysis is finished, you can click on the ‘access result’ button, which will bring you to the data exploration environment.

### Analysis Performance

It might be wondered at what speed the analysis proceeds at. The following plot
shows performance at sample sizes of 6, 12, 24, 48, 96 and 132. These runs
were completed on a computer with two Intel Xeon E5-2698 CPUs running at 2.3 Ghz,
totalling 32 cores with two Hyper-threads per core and 256 GB of RAM. As can be
seen, the runtime for the analysis in this case is roughly linear, with a rate
of roughly 10 samples per hour.

<!-- ![Analysis Performance][analysis_performance] -->
<p class="centered">
<img src="{% static 'userguide/img/performance_plot.png' %}" class="img-thumbnail" alt="Profile page" width="50%" style="float:none;margin:auto;">
</p>

---

# Results

Once your analysis is completed, it will appear in your 'My Projects' page with a green 'Finished' label in your project card.

<!-- ![Project Card][project_card] -->
<p class="centered">
<img src="{% static 'userguide/img/Project_Card.png' %}" class="img-thumbnail" alt="Profile page" width="40%" style="float:none;margin:auto;">
</p>

Click on 'Access Result' to load the data into your browser. A loading screen will appear (please be patient, many projects are quite large!).

<!-- ![Loading Screen][loading_screen] -->
<p class="centered">
<img src="{% static 'userguide/img/loading_screen.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

## Data Environment:

The first page that loads once you select a completed analysis is the Summary Report.

The PiMP Summary Report displays a summary of the key information from the study. ‘Study’ describes the experimental design that has been chosen, the table shows the groups and number of replicates for each group.

<!-- ![Summary Page][summary_page] -->
<p class="centered">
<img src="{% static 'userguide/img/Summary_page.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

### Data Processing

Data Processing describes the algorithms applied to the data, with references.

---

### Quality control

Quality control provides a number of standard methods for assessing the quality of the data: a principal component analysis and the total ion chromatograms for the datasets.

#### Principal Component Analysis

PCA, or principal component analysis is a multivariate statistical method for visualizing large datasets. A good experiment is usually characterized by clear separation between groups. The graph is interactive, and datapoints may be hidden or zoomed in on.

<!-- ![PCA][pca] -->
<p class="centered">
<img src="{% static 'userguide/img/pca.png' %}" class="img-thumbnail" alt="Profile page" width="40%" style="float:none;margin:auto;">
</p>

#### Total Ion Chromatograms

Total ion chromatograms give an overview of the total detected masses from the instrument. In a good experiment, samples should overlay to a large extent in the same group, as in the example below. Often a large broad peak is visible towards the end of the chromatogram: this is usually a consequence of salty samples using HILIC chromatography.

<!-- ![TIC][tic] -->
<p class="centered">
<img src="{% static 'userguide/img/TIC.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

# Results

## Summary Page

Results provides a summary of the key findings from the data for each comparison selected by the user. Data from identified (matched by retention time and mass to a standard) compounds are shown separately from annotated (assigned putatively on the basis of mass) compounds. Only significantly changing compounds are listed here for each group. Peaks are matched by mass by seeing if the peak is within the user definable (in the Change Parameters tab) ppm range and are matched by RT by seeing if the peak is within a user definable percentage of the standard compound.

<!-- ![Result Histgrams][results] -->
<p class="centered">
<img src="{% static 'userguide/img/results.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

### Volcano Plots

Next, a volcano plot graphs fold change vs significance, such that the most significant and highest magnitude changes are in the top left and right of the graph. This graph is also interactive and the points can be clicked on to obtain more information about each peak.

<!-- ![Volcano Plot][volcano] -->
<p class="centered">
<img src="{% static 'userguide/img/volcano.png' %}" class="img-thumbnail" alt="Profile page" width="40%" style="float:none;margin:auto;">
</p>

---

## Metabolites Tab

Most researchers in metabolomics are more interested in metabolites than peaks, per se. For this reason, we decided to provide any metabolite that evidence existed for in the data. The metabolites tab summarises all the information about detected compounds, allowing the researcher to explore metabolites, pathways and their levels in different sample sets.

<!-- ![Metabolites Tab][metabolites] -->
<p class="centered">
<img src="{% static 'userguide/img/Metabolites.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

There is a free text search in the top bar that allows the researcher to narrow down on a particular compound or pathway. One can also sort on any of the columns by clicking on the title bar. Additionally, there are drop-down menus to filter the detected metabolites by pathway or superpathway.

Each experimental comparison is listed in the table next to the name and formula of each metabolite. Levels of the metabolite relative to the control condition are shown as log2 fold changes and colour coded red for upregulated and blue for downregulated. Finally, each metabolite is listed as 'annotated' or 'identified' based on the Metabolite Standards Initiative guidelines.

The 'Evidence' panel on the right of the table, activated by selecting a metabolite, provides all the evidence available for that compound, including the reference database the metabolite was found in (including the standards databases uploaded as part of the setup files), the structure of the compound, and any peak data associated with the compound. Simply click on the 'chromatogram' button <img src="{% static 'userguide/img/chromatogram_icon.svg' %}" alt="Profile page" width="30px" style="float:none;margin:auto;"> to see an interactive plot of the data.

<!-- ![Metabolite Peak][metabolite_peak] -->
<p class="centered">
<img src="{% static 'userguide/img/metabolite_peak.png' %}" class="img-thumbnail" alt="Profile page" width="20%" style="float:none;margin:auto;">
</p>

Additionally, interactive histograms of the peak can be checked below, by clicking the 'intensities' button. <img src="{% static 'userguide/img/intensity_icon.svg' %}" alt="Profile page" width="30px" style="float:none;margin:auto;">

<!-- ![Metabolite intensities][metabolite_int] -->
<p class="centered">
<img src="{% static 'userguide/img/metabolite_int.png' %}" class="img-thumbnail" alt="Profile page" width="20%" style="float:none;margin:auto;">
</p>

**An important thing to bear in mind is the relationship of LC-MS peak to metabolite.**

A single peak often can be matched to a single empirical formula, but each formula can be arranged as several structures, which are indistiguishable by mass alone. For this reason, the same peak may be assigned to multiple metabolites, all of which are displayed in the metabolites table. We have done this to avoid making any erroneous assumptions as to the priority of a metabolite assignment. For those metabolites that match by both retention time and mass, they are listed as 'identified' as that metabolite.

Each metabolite can also match several peaks, as several different structures with the same empirical formula may elute during the chromatographic separation (i.e. they will have different retention times), or may occur in multiple polarities (i.e. both positive and negative). For this reason, each 'evidence tab' may have more than one peak associated with it.
<div style="page-break-after: always;"></div>
---

> *Evidence panel Tips*

> * Peaks matched by retention time and mass to a standard are indicated by this icon  <img src="{% static 'userguide/img/PiMP_logo_compound_id.svg' %}" alt="Profile page" width="20px" style="float:none;margin:auto;">.

> * The number on the top right corner of the 'peak card' indicates the number of other compounds annotated by this peak.

> * A single click on the 'pathway card' gives access to the list of pathways where the metabolite is found.

> * A single click on the title of the 'compound card' gives access to the compound structure.

> * All cards once expanded can be collapsed for better readability

> * All graphics in the evidence panel can be downloaded in different formats by clicking on <img src="{% static 'userguide/img/figure_download_icon.png' %}" class="img-thumbnail" alt="Profile page" width="30px" style="float:none;margin:auto;"> in the top right corner.

---
<div style="page-break-after: always;"></div>
## Metabolic Maps Tab

The metabolic maps tab contains information about the pathways and that metabolites are assigned to. The information in this tab is derived from the Kyoto Encyclopedia of Genes and Genomes database.

<!-- ![Metabolic Maps][maps] -->
<p class="centered">
<img src="{% static 'userguide/img/maps.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Maps are listed along with the total number of compounds in each map, the detected compounds that are listed as either annotated or identified (matched to a mass for the former, or matched to both mass and retention time for the latter), along with a coverage score that describes how much of the pathway has been detected overall.

The list of maps is searchable using the real time search bar at the top of the page.

Clicking on any of the map entries invokes a sidebar containing more information about that map, including the 'Kegg Map button' .

<!-- ![Metabolic Maps Button][maps_button] -->
<p class="centered">
<img src="{% static 'userguide/img/pathway_icon.svg' %}" alt="Kegg button" width="40px" style="float:none;margin:auto;">
</p>

When clicked, the kegg map button will create a new window containing the Kegg map for that particular pathway, along with colour coding of the  metabolites: empty circles are undetected metabolites, gold circles are identified (RT and mass matched) and grey circles are annotated metabolites.

<!-- ![Kegg Map][kegg_map] -->
<p class="centered">
<img src="{% static 'userguide/img/maps_kegg.png' %}" class="img-thumbnail" alt="Profile page" width="60%" style="float:none;margin:auto;">
</p>

To display a quantitative overview for a specific comparison, click on the 'Map Comparison' combo box in the top left hand corner.

<!-- ![Select Comparison][maps_select_comp] -->
<p class="centered">
<img src="{% static 'userguide/img/maps_select_comp.png' %}" class="img-thumbnail" alt="Profile page" width="60%" style="float:none;margin:auto;">
</p>

This will display the same map with rings around the individual metabolites, colour-coded according to the comparison of their levels, with red being upregulated and blue being downregulated.

<!-- ![Map Comparison][maps_comparison] -->
<p class="centered">
<img src="{% static 'userguide/img/maps_comparison.png' %}" class="img-thumbnail" alt="Profile page" width="60%" style="float:none;margin:auto;">
</p>

This allows a rapid overview of the data in the context of pathways, and it may be possible to identifiy metabolic chokepoints or enzymatic inhibition, if metabolites upstream an enzyme are upregulated and those downstream of the same enzyme are downregulated.

## Comparisons Tab

The metabolites tab contains every metabolite for which there is evidence of its existence in the dataset. However, there are many compounds detected in a typical metabolomics analysis (especially in LC-MS) for which no known metabolite can be matched.

The majority of these are likely to be contaminants from plasticware, the atmosphere, sample handling, or (in the case of clinical samples) xenobiotics.

In some cases, however, interesting molecules are detected that may be previously undescribed. It may be worth taking a particular unknown compound forward for further characterisation, although this is very challenging and the resources required to fully characterise an unknown compound can be very significant.

For this reason, the comparison tab provides an overview of all differentially regulated compounds.

<!-- ![Comparison Tab][comparison] -->
<p class="centered">
<img src="{% static 'userguide/img/comparison.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Detected compounds are listed by Peak ID (an arbitrary identifier generated by the software), and can be sorted on any of the columns, *e.g.* based on fold change of a particular comparison.

The sidebar provides detailed information about the peak of interest, including the levels of the compound in the same way as the metabolite tab. Additionally, any annotation determined for the peak is listed at the bottom of the sidebar.

<!-- ![Comparison Sidebar][comparison_sidebar] -->
<p class="centered">
<img src="{% static 'userguide/img/comparison_sidebar.png' %}" class="img-thumbnail" alt="Profile page" width="20%" style="float:none;margin:auto;">
</p>

## Peaks Tab

The peaks tab provide an overview of the 'raw data'. Detected features (following processing and filtering) in the LC-MS data are displayed here.

<!-- ![Peaks Tab][peaks] -->
<p class="centered">
<img src="{% static 'userguide/img/peaks.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Similar to the other tabs, the panel is split into a main window and a sidebar providing detailed information about a specific peak. In the main window, the peak ID, mass and retention time are listed, along with the intensities of each peak in each sample, arranged in groups according to the comparison factors selected in the experimental definition.

The sidebar contains basic information about the peak, the intensities in each sample as an interactive histogram, and the peak chromatogram.

## More tabs

The more tab provides a drop down menu of each comparison. This provides the statistical data for a specific comparison, as well as the typical sidebar providing detailed information about each peak.

<!-- ![More Tab][more_comparison] -->
<p class="centered">
<img src="{% static 'userguide/img/more_comparison.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

You can sort and filter by log fold change, raw p-value, Benjamini and Hochberg corrected p-value and log odds by using the two text boxes at the top of each column (left being the minimum filter and right being the maximum filter).

<!-- ![Filters][more_comparison_filters] -->
<p class="centered">
<img src="{% static 'userguide/img/more_comparison_filters.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>


It's also possible to search for any peak containing a specific number by using the Peak ID search box at the top of the Peak ID column.

<!-- ![ID Filters][more_comparison_id_filters] -->
<p class="centered">
<img src="{% static 'userguide/img/more_comparison_id_filters.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

## Network analysis

PiMP provides basic network analysis (of identified metabolite only) using MetExploreViz plugin. In order to start a network analysis, click on the "Network analysis" button on the left side tools menu. A popup window will appear allowing you to select the biosource and pathways to map your data on. Please note that this plugin is still at its early stage and will offer more mapping options in the future.

<p class="centered">
<img src="{% static 'userguide/img/network_analysis.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

Once the biosource is selected, the drop-down pathway selection is populated, two numbers appear next to each pathway to inform on the number of metabolite in the pathway and the number of metabolite match between brackets. Press the "Launch" button to launch the tool.

<p class="centered">
<img src="{% static 'userguide/img/network_analysis_pathway.png' %}" class="img-thumbnail" alt="Profile page" width="30%" style="float:none;margin:auto;">
</p>

Once launched, a new tab displaying the network appears in the data environment. Several tools are available in order analyse the network and the network iteself can be exported in different format for further analysis and presentation purposes. For more information on how to use MetExploreViz please read the feature section of the <a href="http://metexplore.toulouse.inra.fr/metexploreViz/doc/documentation.php" target="_blank" title="MetExploreViz">documentation</a>.

<p class="centered">
<img src="{% static 'userguide/img/metexploreviz.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>

---

> *Network analysis Tips*

> * You can select as many pathway as necessary when you create your network, however if you are working on big networks (+1000 nodes) we advise to export it and analyse it within a dedicated tool such as <a href="http://www.cytoscape.org/" target="_blank" title="Cytoscape">cytoscape</a> or directly using <a href="http://metexplore.toulouse.inra.fr/joomla3/index.php" target="_blank" title="Cytoscape">MetExplore</a>.

> * The intensity data is directly accessible from the network visualisation tool, just select a condition on the left side panel to overlay the values as color scale on the network.

> * Click on the export button to download high quality images of your network for your presentions and papers.

> * Use the copy network feature <img src="{% static 'userguide/img/copy_network.png' %}" class="img-thumbnail" alt="Profile page" width="30px" style="float:none;margin:auto;"> to easily compare the network under several conditions.

---

## Preference

You can access the preference panel in order to control the chromatogram and bar charts. The preference panel can be accessed from the "tools" menu on the left side of the window.

<p class="centered">
<img src="{% static 'userguide/img/preference.png' %}" class="img-thumbnail" alt="Profile page" width="70%" style="float:none;margin:auto;">
</p>


---

> *Preference Tips*

> * Looking at time course data? Select the line chart otpion and reorder your conditions to display a trend plot.

---



## Finally

We hope that this provides you with enough information to get started with PiMP. We welcome any bug reports, suggestions and comments. Good luck with PiMP!



[project_management]:{% static 'userguide/img/Project_Management.png' %}
[my_projects]:{% static 'userguide/img/My_Projects.png' %}
[create_project]:{% static 'userguide/img/Create_Project_Button.png' %}
[project_dialog]:{% static 'userguide/img/Create_project_dialog.png' %}
[project_administration]:{% static 'userguide/img/project_administration.png' %}
[project_card]:{% static 'userguide/img/Project_Card.png' %}
[calibration_samples]:{% static 'userguide/img/calibration_samples.png' %}
[assign_calibration_samples]:{% static 'userguide/img/Assign_Calibration_samples.png' %}
[assign_qc]:{% static 'userguide/img/assign_qc.png' %}
[search_calib]:{% static 'userguide/img/search_calib.png' %}
[upload_files]:{% static 'userguide/img/upload_files.png' %}
[experiment_definition]:{% static 'userguide/img/experiment_definition.png' %}
[analysis_definition]:{% static 'userguide/img/analysis_definition.png' %}
[analysis_list]:{% static 'userguide/img/analysis_list.png' %}
[loading_screen]:{% static 'userguide/img/loading_screen.png' %}
[summary_page]:{% static 'userguide/img/Summary_page.png' %}
[pca]:{% static 'userguide/img/pca.png' %}
[tic]:{% static 'userguide/img/TIC.png' %}
[results]:{% static 'userguide/img/results.png' %}
[volcano]:{% static 'userguide/img/volcano.png' %}
[metabolites]:{% static 'userguide/img/Metabolites.png' %}
[metabolite_peak]:{% static 'userguide/img/metabolite_peak.png' %}
[metabolite_int]:{% static 'userguide/img/metabolite_int.png' %}
[maps]:{% static 'userguide/img/maps.png' %}
[kegg_map]:{% static 'userguide/img/maps_kegg.png' %}
[maps_button]:{% static 'userguide/img/maps_kegg_button.png' %}
[maps_select_comp]:{% static 'userguide/img/maps_select_comp.png' %}
[maps_comparison]:{% static 'userguide/img/maps_comparison.png' %}
[comparison]:{% static 'userguide/img/comparison.png' %}
[comparison_sidebar]:{% static 'userguide/img/comparison_sidebar.png' %}
[peaks]:{% static 'userguide/img/peaks.png' %}
[more_comparison]:{% static 'userguide/img/more_comparison.png' %}
[more_comparison_filters]:{% static 'userguide/img/more_comparison_filters.png' %}
[more_comparison_id_filters]:{% static 'userguide/img/more_comparison_id_filters.png' %}
