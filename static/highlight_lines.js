function (group) {
    var HIGHLIGHT_COLOR = "#000000";
    var HIGHLIGHT_WEIGHT = 6;
    var shapes = [];
    var lines = [];

    group.eachLayer(function (geojson) {
        geojson.eachLayer(function (layer) {
            var properties = layer.feature.properties;
            if (properties.date_rank !== undefined) {
                shapes.push(layer);
            } else if (properties.distance_meters !== undefined) {
                lines.push(layer);
            }
        });
    });

    function insideRing(point, ring) {
        var inside = false;
        for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) {
            var xi = ring[i][0], yi = ring[i][1];
            var xj = ring[j][0], yj = ring[j][1];
            if (
                (yi > point.lat) !== (yj > point.lat) &&
                point.lng < ((xj - xi) * (point.lat - yi)) / (yj - yi) + xi
            ) {
                inside = !inside;
            }
        }
        return inside;
    }

    function inShape(point, shape) {
        var geometry = shape.feature.geometry;
        var polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
        return polygons.some(function (rings) {
            return insideRing(point, rings[0]);
        });
    }

    function endpoints(line) {
        var points = line.getLatLngs();
        return [points[0], points[points.length - 1]];
    }

    shapes.forEach(function (shape) {
        var connected = lines.filter(function (line) {
            return endpoints(line).some(function (point) {
                return inShape(point, shape);
            });
        });
        var styles = connected.map(function (line) {
            return { color: line.options.color, weight: line.options.weight };
        });

        shape.on("mouseover", function () {
            connected.forEach(function (line) {
                line.setStyle({ color: HIGHLIGHT_COLOR, weight: HIGHLIGHT_WEIGHT });
            });
        });
        shape.on("mouseout", function () {
            connected.forEach(function (line, index) {
                line.setStyle(styles[index]);
            });
        });
    });
}
