# adhocracy3 icon font

1.  Install fontcustom (see <http://fontcustom.com/#installation>)
2.  Add/edit SVG icons in `svg/`
3.  Run `bin/merge_static_directories`
4.  Go to `build/icons/`. This directory contains the merged SVGs from core and theme.
5.  `fontcustom compile -c fontcustom.yml`
6.  The compiled webfont files and SCSS are in `static/fonts/`; A preview is available in `static/preview/`
