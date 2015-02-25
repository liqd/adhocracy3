import _ = require("lodash");


export var countries : {
    name: string;
    code: string;
}[] = [

// All countries from here: http://de.wikipedia.org/wiki/Liste_der_Staaten_der_Erde
/*{name: "Afghanistan", code:"AF"}
{name: "Albania", code:"AL"}
{name: "Algeria", code:"DZ"}
{name: "American Samoa", code:"AS"}
{name: "Andorra", code:"AD"}
{name: "Angola", code:"AO"}
{name: "Argentina", code:"AR"}
{name: "Armenia", code:"AM"}
{name: "Australia", code:"AU"}
{name: "Austria", code:"AT"}
{name: "Azerbaijan", code:"AZ"}
{name: "Bahamas", code:"BS"}
{name: "Bahrain", code:"BH"}
{name: "Bangladesh", code:"BD"}
{name: "Barbados", code:"BB"}
{name: "Belarus", code:"BY"}
{name: "Belgium", code:"BE"}
{name: "Belize", code:"BZ"}
{name: "Benin", code:"BJ"}
{name: "Bhutan", code:"BT"}
{name: "Bolivia", code:"BO"}
{name: "Bosnia and Herzegovina", code:"BA"}
{name: "Botswana", code:"BW"}
{name: "Brazil", code:"BR"}
{name: "Brunei", code:"BN"}
{name: "Bulgaria", code:"BG"}
{name: "Burkina Faso", code:"BF"}
{name: "Burundi", code:"BI"}
{name: "Cambodia", code:"KH"}
{name: "Cameroon", code:"CM"}
{name: "Canada", code:"CA"}
{name: "Cape Verde", code:"CV"}
{name: "Central African Republic", code:"CF"}
{name: "Chile", code:"CL"}
{name: "China", code:"CN"}
{name: "Colombia", code:"CO"}
{name: "Comoros", code:"KM"}
{name: "Cook Islands", code:"CK"}
{name: "Costa Rica", code:"CR"}
{name: "Croatia", code:"HR"}
{name: "Cuba", code:"CU"}
{name: "Cyprus", code:"CY"}
{name: "Czech Republic", code:"CZ"}
{name: "Democratic Republic of Congo", code:"CD"}
{name: "Denmark", code:"DK"}
{name: "Djibouti", code:"DJ"}
{name: "Dominica", code:"DM"}
{name: "Dominican Republic", code:"DO"}
{name: "East Timor", code:"TL"}
{name: "Ecuador", code:"EC"}
{name: "Egypt", code:"EG"}
{name: "El Salvador", code:"SV"}
{name: "Equatorial Guinea", code:"GQ"}
{name: "Eritrea", code:"ER"}
{name: "Estonia", code:"EE"}
{name: "Ethiopia", code:"ET"}
{name: "Falkland Islands", code:"FK"}
{name: "Faroe Islands", code:"FO"}
{name: "Fiji", code:"FJ"}
{name: "Finland", code:"FI"}
{name: "France", code:"FR"}
{name: "Gabon", code:"GA"}
{name: "Gambia", code:"GM"}
{name: "Georgia", code:"GE"}
{name: "Germany", code:"DE"}
{name: "Ghana", code:"GH"}
{name: "Greece", code:"GR"}
{name: "Guam", code:"GU"}
{name: "Guatemala", code:"GT"}
{name: "Guinea", code:"GN"}
{name: "Guinea-Bissau", code:"GW"}
{name: "Guyana", code:"GY"}
{name: "Haiti", code:"HT"}
{name: "Honduras", code:"HN"}
{name: "Hungary", code:"HU"}
{name: "Iceland", code:"IS"}
{name: "India", code:"IN"}
{name: "Indonesia", code:"ID"}
{name: "Iran", code:"IR"}
{name: "Iraq", code:"IQ"}
{name: "Ireland", code:"IE"}
{name: "Israel", code:"IL"}
{name: "Italy", code:"IT"}
{name: "Ivory Coast", code:"CI"}
{name: "Jamaica", code:"JM"}
{name: "Japan", code:"JP"}
{name: "Jordan", code:"JO"}
{name: "Kazakhstan", code:"KZ"}
{name: "Kenya", code:"KE"}
{name: "Kiribati", code:"KI"}
{name: "Kuwait", code:"KW"}
{name: "Kyrgyzstan", code:"KG"}
{name: "Laos", code:"LA"}
{name: "Latvia", code:"LV"}
{name: "Lebanon", code:"LB"}
{name: "Lesotho", code:"LS"}
{name: "Liberia", code:"LR"}
{name: "Libya", code:"LY"}
{name: "Liechtenstein", code:"LI"}
{name: "Lithuania", code:"LT"}
{name: "Luxembourg", code:"LU"}
{name: "Macedonia", code:"MK"}
{name: "Madagascar", code:"MG"}
{name: "Malawi", code:"MW"}
{name: "Malaysia", code:"MY"}
{name: "Maldives", code:"MV"}
{name: "Mali", code:"ML"}
{name: "Malta", code:"MT"}
{name: "Marshall Islands", code:"MH"}
{name: "Mauritania", code:"MR"}
{name: "Mauritius", code:"MU"}
{name: "Mexico", code:"MX"}
{name: "Micronesia", code:"FM"}
{name: "Moldova", code:"MD"}
{name: "Monaco", code:"MC"}
{name: "Mongolia", code:"MN"}
{name: "Montenegro", code:"ME"}
{name: "Morocco", code:"MA"}
{name: "Mozambique", code:"MZ"}
{name: "Myanmar", code:"MM"}
{name: "Namibia", code:"NA"}
{name: "Nauru", code:"NR"}
{name: "Nepal", code:"NP"}
{name: "Netherlands", code:"NL"}
{name: "New Zealand", code:"NZ"}
{name: "Nicaragua", code:"NI"}
{name: "Niger", code:"NE"}
{name: "Nigeria", code:"NG"}
{name: "Niue", code:"NU"}
{name: "North Korea", code:"KP"}
{name: "Norway", code:"NO"}
{name: "Oman", code:"OM"}
{name: "Pakistan", code:"PK"}
{name: "Palau", code:"PW"}
{name: "Panama", code:"PA"}
{name: "Papua New Guinea", code:"PG"}
{name: "Paraguay", code:"PY"}
{name: "Peru", code:"PE"}
{name: "Philippines", code:"PH"}
{name: "Poland", code:"PL"}
{name: "Portugal", code:"PT"}
{name: "Puerto Rico", code:"PR"}
{name: "Qatar", code:"QA"}
{name: "Republic of the Congo", code:"CG"}
{name: "Romania", code:"RO"}
{name: "Russia", code:"RU"}
{name: "Rwanda", code:"RW"}
{name: "Saint Kitts and Nevis", code:"KN"}
{name: "Saint Lucia", code:"LC"}
{name: "Saint Vincent and the Grenadines", code:"VC"}
{name: "Samoa", code:"WS"}
{name: "San Marino", code:"SM"}
{name: "Sao Tome and Principe", code:"ST"}
{name: "Saudi Arabia", code:"SA"}
{name: "Senegal", code:"SN"}
{name: "Serbia", code:"RS"}
{name: "Seychelles", code:"SC"}
{name: "Sierra Leone", code:"SL"}
{name: "Singapore", code:"SG"}
{name: "Slovakia", code:"SK"}
{name: "Slovenia", code:"SI"}
{name: "Solomon Islands", code:"SB"}
{name: "Somalia", code:"SO"}
{name: "South Africa", code:"ZA"}
{name: "South Korea", code:"KR"}
{name: "South Sudan", code:"SS"}
{name: "Spain", code:"ES"}
{name: "Sri Lanka", code:"LK"}
{name: "Sudan", code:"SD"}
{name: "Suriname", code:"SR"}
{name: "Swaziland", code:"SZ"}
{name: "Sweden", code:"SE"}
{name: "Switzerland", code:"CH"}
{name: "Syria", code:"SY"}
{name: "Taiwan", code:"TW"}
{name: "Tajikistan", code:"TJ"}
{name: "Tanzania", code:"TZ"}
{name: "Thailand", code:"TH"}
{name: "Togo", code:"TG"}
{name: "Trinidad and Tobago", code:"TT"}
{name: "Tunisia", code:"TN"}
{name: "Turkey", code:"TR"}
{name: "Turkmenistan", code:"TM"}
{name: "Tuvalu", code:"TV"}
{name: "Uganda", code:"UG"}
{name: "Ukraine", code:"UA"}
{name: "United Arab Emirates", code:"AE"}
{name: "United Kingdom", code:"GB"}
{name: "United States", code:"US"}
{name: "Uruguay", code:"UY"}
{name: "Uzbekistan", code:"UZ"}
{name: "Vanuatu", code:"VU"}
{name: "Vatican", code:"VA"}
{name: "Venezuela", code:"VE"}
{name: "Vietnam", code:"VN"}
{name: "Western Sahara", code:"EH"}
{name: "Yemen", code:"YE"}
{name: "Zambia", code:"ZM"}
{name: "Zimbabwe", code:"ZW"}
*/


// European Countries
{name: "Albania", code: "AL"},
{name: "Andorra", code: "AD"},
{name: "Armenia", code: "AM"},
{name: "Austria", code: "AT"},
{name: "Azerbaijan", code: "AZ"},
{name: "Belarus", code: "BY"},
{name: "Belgium", code: "BE"},
{name: "Bosnia and Herzegovina", code: "BA"},
{name: "Bulgaria", code: "BG"},
{name: "Croatia", code: "HR"},
{name: "Cyprus", code: "CY"},
{name: "Denmark", code: "DK"},
{name: "Estonia", code: "EE"},
{name: "Finland", code: "FI"},
{name: "France", code: "FR"},
{name: "Georgia", code: "GE"},
{name: "Germany", code: "DE"},
{name: "Greece", code: "GR"},
{name: "Hungary", code: "HU"},
{name: "Ireland", code: "IE"},
{name: "Iceland", code: "IS"},
{name: "Italy", code: "IT"},
{name: "Kosovo", code: "XK"},
{name: "Latvia", code: "LV"},
{name: "Liechtenstein", code: "LI"},
{name: "Lithuania", code: "LT"},
{name: "Luxembourg", code: "LU"},
{name: "Macedonia, The Former Yugoslav Republic of", code: "MK"},
{name: "Malta", code: "MT"},
{name: "Moldova, Republic of", code: "MD"},
{name: "Monaco", code: "MC"},
{name: "Montenegro", code: "CS"},
{name: "Netherlands", code: "NL"},
{name: "Norway", code: "NO"},
{name: "Poland", code: "PL"},
{name: "Portugal", code: "PT"},
{name: "Romania", code: "RO"},
{name: "Russia", code: "RU"},
{name: "San Marino", code: "SM"},
{name: "Sweden", code: "SE"},
{name: "Switzerland", code: "CH"},
{name: "Serbia" , code: "RS"},
{name: "Slovakia", code: "SK"},
{name: "Slovenia", code: "SI"},
{name: "Spain", code: "ES"},
{name: "Czech Republic", code: "CZ"},
{name: "Turkey", code: "TR"},
{name: "Ukraine", code: "UA"},
{name: "United Kingdom", code: "GB"},
{name: "Vatican City State", code: "VA"},
];


export var countrySelect = () => {
    return {
        scope: {
            name: "@",
            required: "@",
            value: "=ngModel"
        },
        restrict: "E",
        template:
            (elm, attr) => {
                attr.star = (attr.required === "required") ? "*" : "";
                return "<select data-ng-model=\"value\" name=\"{{name}}\"" +
                "       data-ng-options=\"c.code as c.name for c in countries\" data-ng-required=\"required\">" +
                "           <option value=\"\" selected>{{ 'TR__COUNTRY' | translate }}" + attr.star + "</option>" +
                "</select>";
            },
        link: (scope) => {
            scope.countries = countries;
        }
    };
};


export var countryName = () => (code) => {
    var candidates = _.filter(countries, (i) => i.code === code);
    return candidates.length !== 0 ? candidates[0].name : code;
};


/**
 * A service to wrap parts of a string in templates.
 *
 * wrap.replace("Hello [[:World]]!");
 * -> "Hello World!"
 *
 * wrap.replace("Hello [[link:World]]!", {
 *   link: "<a>{{content}}</a>"
 * });
 * -> "Hello <a>World</a>!"
 */
export class Wrap {
    private openMarker : string = "[";
    private closeMarker : string = "]";
    private keySeparator : string = ":";
    private escapeMarker : string = "\\";

    constructor(private $interpolate) {}

    public encode(msg : string) : string {
        return msg
            .replace(this.openMarker, this.escapeMarker + this.openMarker)
            .replace(this.closeMarker, this.escapeMarker + this.closeMarker);
    }

    public decode(msg : string) : string {
        return msg
            .replace(this.escapeMarker + this.openMarker, this.openMarker)
            .replace(this.escapeMarker + this.closeMarker, this.closeMarker);
    }

    public wrap(msg : string, templates) : string {
        var a = msg.split(this.openMarker + this.openMarker);
        if (a.length < 2) {
            return msg;
        }
        var before = a.shift();
        var after = a.join(this.openMarker + this.openMarker);

        var b = after.split(this.closeMarker + this.closeMarker);
        if (b.length < 2) {
            throw "No matching closing marker found in " + msg;
        }
        var inside = b.shift();
        after = b.join(this.closeMarker + this.closeMarker);

        var c = inside.split(this.keySeparator);
        if (c.length < 2) {
            throw "No key seperator found in " + msg;
        }
        var key = c.shift();
        inside = c.join(this.keySeparator);

        var template = templates[key];
        if (typeof template !== "undefined") {
            inside = this.$interpolate(template)({
                content: inside
            });
        }

        return before + inside + this.wrap(after, templates);
    }
}


/**
 * Translate directive for strings that contain HTML.
 *
 * Imagine you want to translate some HTML like this:
 *
 *     Click <a href="#">here</a>!
 *
 * The issue of course is that a part of the string is wrapped in HTML.
 * With plain translation, you can not easily translate this. Your only
 * option is to split this into several translatable strings which might
 * not work in some languages.
 *
 * This directive tries to solve the problem by using adhWrap. So the
 * above could be written like this:
 *
 *     <span adh-html-translate="Click [[link:here]]!" translate-templates="{
 *         link: '&lt;a href=&quot;#&quot;&gt;{{content}}&lt;/a&gt;'
 *     }"></span>
 */
export var htmlTranslateDirective = ($translate, adhWrap : Wrap) => {
    return {
        restrict: "A",
        scope: {
            translateValues: "=?",
            translateTemplates: "=?"
        },
        link: (scope, element, attrs) => {
            // NOTE: we could use another element for this
            var escapeHTML = (s : string) => element.text(s).html();

            var update = () => {
                var msg = attrs.adhHtmlTranslate || "";
                var values = scope.translateValues || {};
                var templates = scope.translateTemplates || {};

                // FIXME: adhWrap.encode values before interpolating
                $translate(msg, values).then((translated : string) => {
                    var html = escapeHTML(translated);
                    var wrapped = adhWrap.decode(adhWrap.wrap(html, templates));
                    // FIXME: do some $sce related magic here
                    element.html(wrapped);
                });
            };

            scope.$watch(() => attrs.htmlTranslate, update);
            scope.$watch("translateValues", update);
            scope.$watch("translateTemplates", update);
        }
    };
};


export var moduleName = "adhLocale";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .filter("adhCountryName", countryName)
        .service("adhWrap", ["$interpolate", Wrap])
        .directive("adhHtmlTranslate", ["$translate", "adhWrap", htmlTranslateDirective])
        .directive("countrySelect", ["adhConfig", countrySelect]);
};
