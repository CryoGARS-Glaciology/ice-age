function (group) {
    var HIGHLIGHT_COLOR = "#000000";
    var HIGHLIGHT_WEIGHT = 6;
    var shapes = [];
    var lines = [];
    var hoverLines = [];
    var dots = [];

    group.eachLayer(function (geojson) {
        geojson.eachLayer(function (layer) {
            var properties = layer.feature.properties;
            if (properties.date_rank !== undefined) {
                shapes.push(layer);
            } else if (layer.getRadius) {
                dots.push(layer);
            } else if (properties.distance_meters !== undefined && layer.getLatLngs) {
                if (layer.options.opacity > 0) {
                    lines.push(layer);
                } else {
                    hoverLines.push(layer);
                }
            }
        });
    });

    function setDots(iceberg, visible) {
        dots.forEach(function (dot) {
            if (dot.feature.properties.IcebergID === iceberg) {
                dot.setStyle(visible ? { opacity: 1, fillOpacity: 1 } : { opacity: 0, fillOpacity: 0 });
            }
        });
    }

    shapes.forEach(function (shape) {
        var connected = lines.filter(function (line) {
            return line.feature.properties.IcebergID === shape.feature.properties.IcebergID;
        });
        var styles = connected.map(function (line) {
            return { color: line.options.color, weight: line.options.weight };
        });

        shape.on("mouseover", function () {
            connected.forEach(function (line) {
                line.setStyle({ color: HIGHLIGHT_COLOR, weight: HIGHLIGHT_WEIGHT });
            });
            setDots(shape.feature.properties.IcebergID, true);
        });
        shape.on("mouseout", function () {
            connected.forEach(function (line, index) {
                line.setStyle(styles[index]);
            });
            setDots(shape.feature.properties.IcebergID, false);
        });
    });

    // The invisible hover line over each connecting line also shows its dots
    hoverLines.forEach(function (hoverLine) {
        var iceberg = hoverLine.feature.properties.IcebergID;
        hoverLine.on("mouseover", function () {
            setDots(iceberg, true);
        });
        hoverLine.on("mouseout", function () {
            setDots(iceberg, false);
        });
    });
}
