# PeakPeek

A script based on UnityPy to build a map of a given [PEAK](https://landfall.se/peak) level features.

<img src="/level12.png" height=256 title="Example output" />

### Usage:
```console
$ ./PeakPeek.py …/PEAK_Data/levelN
```
Usually, $N = 5+X$, where $X$ is the number from the ingame «Level_X».

The result is saved as `./levelN.png`.

Can be run in parallel using e.g. `xargs` to process multiple/all levels. A suitable glob would be `level?{,?}`.

### Icons:
As I'm uncertain on the origin of the Wiki icons, I'm using a folder structure compatible with [lane_ftw's ItemFinder mod](https://thunderstore.io/c/peak/p/lane_ftw/ItemFinder) resources.
Just copy all `Icons/` contents to `icons/` directory next to the script and it will do.

---
Made for https://peak.wiki.gg/wiki/Daily.
