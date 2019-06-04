2016 SenSys Paper
=================

This folder contains the data from the [2016 SenSys paper](https://patpannuto.com/pubs/kempke16surepoint.pdf).

These experiments were run throughout the course of the day (actually a few
days) in the generally well-populated atrium of the Bob and Betty Beyster
Building at the University of Michigan, Ann Arbor campus.

The Data
--------

There are two experiments in this dataset. The first is a series of runs to
generate the "cross" plot, that is a standing individual at a series of fixed
points moving across the floor. The `cross4` experiment is reported in the
paper. I unfortunately do not remember what went wrong with cross 1-3, and the
data should probably be treated as dubious.

The second experiment is a motion experiment, where I ran around with the tag
on a pole I was holding. There should be a decent amount of XY variance and a
modest amount of Z variance. I think the final trace we used spells `Poly` in
reasonable cursive when plotted, sadly none of the `Pat` takes came out.
We took quite a few traces for this too if memory serves, but our data archive
has just the one `motion` folder, so I'm not sure what happened to the rest.

### Diving in

> Advance note: I'd really hoped to clean this up more. I did a decent job of
> cleaning up the PolyPoint stuff.., but at this point it's better to get
> something out for folks to play with if they're interested. As a consequence,
> this is a bit of a dump, apologies. Maybe some day I will have the time to
> make it better. I'm putting it all in an `alldata` folder for now with the
> optimistic dream of cleaning it up more in the future.

It's a bit messy, but I think the best way to dive in would be the data in the
"cross-proc" folder, as it's already processed and parsed. The files with
ranges are things like "full-1.df.22", which is for position #1 all 30 range
estimates between node id `df` (the tag) and node id `22` (an anchor) [note not
all ranges succeed, there are nan's].

This data corresponds to Figure 8 from the SurePoint paper, the "proc2.py" file
shows how to translate position index to x,y,z location as well as ground truth
for the anchors.

Surepoint's algorithm chooses the 12th percentile of all the range estimates it
sees for the "true" range: We take the 12th percentile of the range estimates.
We also do linear interpolation to get a slightly more precise version (i.e. if
the 12th percentile index of the array would be 3.4 we compute ranges[3] + .4 *
(ranges[4] - ranges[3])).  Matlab's prctile does this out of the box, so
prctile(ranges, 12) should give you our average.


---

```bibtex
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

