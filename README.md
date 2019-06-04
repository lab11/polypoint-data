Datasets from the PolyPoint & SurePoint Projects
================================================

[![License: CC BY 4.0](https://licensebuttons.net/l/by/4.0/80x15.png)](https://creativecommons.org/licenses/by/4.0/)

This repository is a collection of the major datasets from the
[PolyPoint and subsequently SurePoint projects](https://github.com/lab11/polypoint).
We've made a reasonable effort to document each of the major collections, but
they'll vary a bit in the format, quality, and consistency -- much of this
repository is a post-hoc collection of data saved/found on folks' machines.
Please do check out the README in each trace for details.


The Data
--------
The dataset consists of a timestamp, ground truth X, Y, and Z coordinates, and
range estimates between nodes in complex indoor environments.  For each
location, there are (up to) twenty seven range estimates, from the selection of
one of three RF channels, one of three transmitting antennas, and one of three
receiving antennas (3×3×3=27).


Licensing, Attribution, Etc
---------------------------
[This work is licensed under a Creative Commons Attribution 4.0 International License.](https://creativecommons.org/licenses/by/4.0/)

For formal citations, please use [the DATA'18 paper](https://patpannuto.com/pubs/pannuto18uwbdata.pdf) for the dataset itself
or [the SenSys'16 paper](https://patpannuto.com/pubs/kempke16surepoint.pdf) for the underlying ranging system, hardware, etc.

```bibtex
@inproceedings{pannuto18uwbdata,
	title = {Indoor Ultra Wideband Ranging Samples from the {DecaWave} {DW1000} Including Frequency and Polarization Diversity},
	booktitle = {Data Acquisition To Analysis},
	series = {DATA'18},
	year = {2018},
	month = {11},
	conference-url = {https://workshopdata.github.io/DATA2018/},
	author = {Pannuto, Pat and Kempke, Benjamin and Campbell, Bradford and Dutta, Prabal},
}

@inproceedings{kempke16surepoint,
	title = {{SurePoint}: Exploiting Ultra Wideband Flooding and Diversity to Provide Robust, Scalable, High-Fidelity Indoor Localization},
	booktitle = {Proceedings of the 14th ACM Conference on Embedded Networked Sensor Systems},
	series = {SenSys'16},
	year = {2016},
	month = {11},
	location = {Stanford, CA, USA},
	conference-url = {http://sensys.acm.org/2016/},
	author = {Kempke, Benjamin and Pannuto, Pat and Campbell, Bradford and Dutta, Prabal},
}
```
