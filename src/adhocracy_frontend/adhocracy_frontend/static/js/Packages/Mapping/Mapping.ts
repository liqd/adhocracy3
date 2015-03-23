export var mapinput = ($timeout, L) => {
    return {
        scope: {
            lat : "=",
            lng : "="
        },
        restrict: "E",
        template: "<div class=\"map\" style=\"cursor:crosshair;\"></div>",
        link: (scope, element, attrs) => {
            var mapElement = element.find(".map");
            mapElement.height(attrs.height);

            var map = L.map(mapElement[0], {
                center: [attrs.lat, attrs.lng],
                zoom: 14
            });
            map.clicked = 0;
            L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);

            var marker = L.marker([scope.lat, scope.lng], {draggable: true});
            map.on("click", (event) => {
                map.clicked = map.clicked + 1;
                setTimeout(() => {
                    if (map.clicked === 1) {
                        marker.setLatLng(event.latlng);
                        marker.addTo(map);
                        $timeout( () => {
                            scope.lat = event.latlng.lat;
                            scope.lng = event.latlng.lng;
                        });
                        map.clicked = 0;
                    }
                }, 200);
            });
            map.on("dblclick", (event) => {
                map.clicked = 0;
                map.zoomIn();
            });
            marker.on("dragend", (event) => {
                var result = event.target.getLatLng();
                $timeout(function() {
                    scope.lat = result.lat;
                    scope.lng = result.lng;
                });
            });
        }
    };
};

export var mapdetail = (L) => {
    return {
        scope: {
            lat : "=",
            lng : "="
        },
        restrict: "E",
        template: "<div class=\"map\"></div>",
        link: (scope, element, attrs) => {
            var mapElement = element.find(".map");
            mapElement.height(attrs.height);

            var map = L.map(mapElement[0], {
                center: [attrs.lat, attrs.lng],
                zoom: 14
            });
            L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);
            L.marker([scope.lat, scope.lng]).addTo(map);
        }
    };
};


export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhMapInput", ["$timeout", "leaflet", mapinput])
        .directive("adhMapDetail", ["leaflet", mapdetail]);
};
