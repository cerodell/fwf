/*
        Leaflet.OpacityControls, a plugin for adjusting the opacity of a Leaflet map.
        (c) 2013, Jared Dominguez
        (c) 2013, LizardTech

        https://github.com/lizardtechblog/Leaflet.OpacityControls
*/

//Declare global variables
var opacity_layer;
var opacity_layer_group;

//Create a control to increase the opacity value. This makes the image more opaque.
L.Control.higherOpacity = L.Control.extend({
    options: {
        position: 'topright'
    },
    setOpacityLayer: function (layer) {
            opacity_layer = layer;
    },
    onAdd: function () {
        
        var higher_opacity_div = L.DomUtil.create('div', 'higher_opacity_control');

        L.DomEvent.addListener(higher_opacity_div, 'click', L.DomEvent.stopPropagation)
            .addListener(higher_opacity_div, 'click', L.DomEvent.preventDefault)
            .addListener(higher_opacity_div, 'click', function () { onClickHigherOpacity() });
        
        return higher_opacity_div;
    }
});

//Create a control to decrease the opacity value. This makes the image more transparent.
L.Control.lowerOpacity = L.Control.extend({
    options: {
        position: 'topright'
    },
    setOpacityLayer: function (layer) {
            opacity_layer = layer;
    },
    onAdd: function (map) {
        
        var lower_opacity_div = L.DomUtil.create('div', 'lower_opacity_control');

        L.DomEvent.addListener(lower_opacity_div, 'click', L.DomEvent.stopPropagation)
            .addListener(lower_opacity_div, 'click', L.DomEvent.preventDefault)
            .addListener(lower_opacity_div, 'click', function () { onClickLowerOpacity() });
        
        return lower_opacity_div;
    }
});

//Create a jquery-ui slider with values from 0 to 100. Match the opacity value to the slider value divided by 100.
L.Control.opacitySlider = L.Control.extend({
    options: {
        position: 'topright'
    },
    setOpacityLayer: function (layer) {
            opacity_layer = layer;
    },
    onAdd: function (map) {
        var opacity_slider_div = L.DomUtil.create('div', 'opacity_slider_control');
        
        $(opacity_slider_div).slider({
          orientation: "vertical",
          range: "min",
          min: 20,
          max: 90,
          value: 70,
          step: 10,
          start: function ( event, ui) {
            //When moving the slider, disable panning.
            map.dragging.disable();
            map.once('mousedown', function (e) { 
              map.dragging.enable();
            });
          },
          slide: function ( event, ui ) {
            var slider_value = ui.value / 100;
            opacity_layer.setOpacity(slider_value);
          }
        });

        // Hacks to give the slider a title and override CSSS
        opacity_slider_div.title = "Change opacity"
        opacity_slider_div.style = "margin-top: 15px; margin-right: 15px;"
        
        return opacity_slider_div;
    }
});


function onClickHigherOpacity() {
    var opacity_value = opacity_layer.options.opacity;
    
    if (opacity_value > 1) {
        return;
    } else {
        opacity_layer.setOpacity(opacity_value + 0.2);
        //When you double-click on the control, do not zoom.
        map.doubleClickZoom.disable();
        map.once('click', function (e) { 
            map.doubleClickZoom.enable();
        });
    }

}

function onClickLowerOpacity() {
    var opacity_value = opacity_layer.options.opacity;
    
    if (opacity_value < 0) {
        return;
    } else {
        opacity_layer.setOpacity(opacity_value - 0.2);
        //When you double-click on the control, do not zoom.
        map.doubleClickZoom.disable();
        map.once('click', function (e) { 
            map.doubleClickZoom.enable();
        });
    }
      
}

// Control opacity of multiple layers with one control
// per https://github.com/lizardtechblog/Leaflet.OpacityControls/issues/6
L.Control.opacitySliderGroup = L.Control.extend({
    options: {
        position: 'topright'
    },
    setOpacityLayerGroup: function (layerGroup) {
            opacity_layer_group = layerGroup;
    },
    onAdd: function (map) {
        var opacity_slider_div = L.DomUtil.create('div', 'opacity_slider_control');
        
        $(opacity_slider_div).slider({
          orientation: "vertical",
          range: "min",
          min: 20,
          max: 90,
          value: 70,
          step: 10,
          start: function ( event, ui) {
            //When moving the slider, disable panning.
            map.dragging.disable();
            map.once('mousedown', function (e) { 
              map.dragging.enable();
            });
          },
          slide: function ( event, ui ) {
            var slider_value = ui.value / 100;
            _setOpacityToLayerGroup(opacity_layer_group, slider_value);
          }
        });
        
        // Hacks to give the slider a title and override CSSS
        opacity_slider_div.title = "Change opacity"
        opacity_slider_div.style = "margin-top: 15px; margin-right: 15px;"
        
        return opacity_slider_div;
    }
});

function _setOpacityToLayerGroup(layerGroup, sliderValue) {
     var index = 0;
     var layersInGroup = layerGroup.getLayers();
        for (index = 0; index < layersInGroup.length; ++index) {
            layersInGroup[index].setOpacity(sliderValue);
        }        
}
