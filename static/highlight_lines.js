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
            } else if (
                properties.distance_meters !== undefined &&
                layer.getLatLngs &&
                layer.options.opacity > 0
            ) {
                lines.push(layer);
            }
        });
    });

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
        });
        shape.on("mouseout", function () {
            connected.forEach(function (line, index) {
                line.setStyle(styles[index]);
            });
        });
    });
}
