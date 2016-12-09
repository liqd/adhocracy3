# adhocracy3 icon font

1.  Install fontcustom (see <https://github.com/FontCustom/fontcustom>)
2.  Add/edit SVG icons in `svg/`
3.  Run `bin/ad_merge_static_directories`
4.  Go to `build/icons/`. This directory contains the merged SVGs from core and theme.
5.  `fontcustom compile -c fontcustom.yml`
6.  The compiled webfont files and SCSS are in `static/fonts/`; A preview is available in `static/preview/`

# Fallback codepoints

In order to be screen-reader friendly, fontcustom by default uses unicode's
private use areas which do not have any semantics.

However, it may be useful to use other unicode codepoints for the icons.  This
way, an appropriate icon from the system font will be used if the iconfont
cannot be loaded (e.g. because of a company firewall). Example: An envolpe icon
might use codepoint U+2709.

A codepoint can be selected by adding it to `.fontcustom-manifest.json`. Other
changes to this file should not be comitted to git.

You can find codepoints using services such as <http://unicode-table.com/>.
