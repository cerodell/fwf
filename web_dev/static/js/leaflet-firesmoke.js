// Per http://apps.socib.es/Leaflet.TimeDimension/examples/example10.html

L.TimeDimension.Layer.ImageOverlay = L.TimeDimension.Layer.extend({

    initialize: function(layer, options) {
        L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
        this._layers = {};
        this._defaultTime = 0;
        this._timeCacheBackward = this.options.cacheBackward || this.options.cache || 0;
        this._timeCacheForward = this.options.cacheForward || this.options.cache || 0;
        this._getUrlFunction = this.options.getUrlFunction;

        this._baseLayer.on('load', (function() {
            this._baseLayer.setLoaded(true);
            this.fire('timeload', {
                time: this._defaultTime
            });
        }).bind(this));
    },

    eachLayer: function(method, context) {
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                method.call(context, this._layers[prop]);
            }
        }
        return L.TimeDimension.Layer.prototype.eachLayer.call(this, method, context);
    },

    _onNewTimeLoading: function(ev) {
        var layer = this._getLayerForTime(ev.time);
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
        }
    },

    isReady: function(time) {
        var layer = this._getLayerForTime(time);
        return layer.isLoaded();
    },

    _update: function() {
        if (!this._map)
            return;
        var time = map.timeDimension.getCurrentTime();
        var layer = this._getLayerForTime(time);
        if (this._currentLayer == null) {
            this._currentLayer = layer;
        }
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
        } else {
            this._showLayer(layer, time);
        }
    },

    _showLayer: function(layer, time) {
        if (this._currentLayer && this._currentLayer !== layer) {
            this._currentLayer.hide();
            this._map.removeLayer(this._currentLayer);
        }
        layer.show();
        if (this._currentLayer && this._currentLayer === layer) {
            return;
        }
        this._currentLayer = layer;
        // Cache management
        var times = this._getLoadedTimes();
        var strTime = String(time);
        var index = times.indexOf(strTime);
        var remove = [];
        // remove times before current time
        if (this._timeCacheBackward > -1) {
            var objectsToRemove = index - this._timeCacheBackward;
            if (objectsToRemove > 0) {
                remove = times.splice(0, objectsToRemove);
                this._removeLayers(remove);
            }
        }
        if (this._timeCacheForward > -1) {
            index = times.indexOf(strTime);
            var objectsToRemove = times.length - index - this._timeCacheForward - 1;
            if (objectsToRemove > 0) {
                remove = times.splice(index + this._timeCacheForward + 1, objectsToRemove);
                this._removeLayers(remove);
            }
        }
    },

    _getLayerForTime: function(time) {
        if (time == 0 || time == this._defaultTime) {
            return this._baseLayer;
        }
        if (this._layers.hasOwnProperty(time)) {
            return this._layers[time];
        }
        var url = this._getUrlFunction(this._baseLayer.getURL(), time);
        imageBounds = this._baseLayer._bounds;

        var newLayer = L.imageOverlay(url, imageBounds, this._baseLayer.options);
        this._layers[time] = newLayer;
        newLayer.on('load', (function(layer, time) {
            layer.setLoaded(true);
            if (map.timeDimension && time == map.timeDimension.getCurrentTime() && !map.timeDimension.isLoading()) {
                this._showLayer(layer, time);
            }
            this.fire('timeload', {
                time: time
            });
        }).bind(this, newLayer, time));

        // Hack to hide the layer when added to the map.
        // It will be shown when timeload event is fired from the map (after all layers are loaded)
        newLayer.onAdd = (function(map) {
            Object.getPrototypeOf(this).onAdd.call(this, map);
            this.hide();
        }).bind(newLayer);
        return newLayer;
    },

    _getLoadedTimes: function() {
        var result = [];
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                result.push(prop);
            }
        }
        return result.sort();
    },

    _removeLayers: function(times) {
        for (var i = 0, l = times.length; i < l; i++) {
            this._map.removeLayer(this._layers[times[i]]);
            delete this._layers[times[i]];
        }
    },

});

L.timeDimension.layer.imageOverlay = function(layer, options) {
    return new L.TimeDimension.Layer.ImageOverlay(layer, options);
};

L.ImageOverlay.include({
    _visible: true,
    _loaded: false,

    _originalUpdate: L.imageOverlay.prototype._update,

    _update: function() {
        if (!this._visible && this._loaded) {
            return;
        }
        this._originalUpdate();
    },

    setLoaded: function(loaded) {
        this._loaded = loaded;
    },

    isLoaded: function() {
        return this._loaded;
    },

    hide: function() {
        this._visible = false;
        if (this._image && this._image.style)
            this._image.style.display = 'none';
    },

    show: function() {
        this._visible = true;
        if (this._image && this._image.style)
            this._image.style.display = 'block';
    },

    getURL: function() {
        return this._url;
    },

});

pad2 = function (n) {
    return n < 10 ? '0' + n : n;
};

dateFileName = function (time) {
    YYYYMMDD = time.getUTCFullYear().toString();
    YYYYMMDD += pad2(time.getUTCMonth() + 1).toString();
    YYYYMMDD += pad2(time.getUTCDate()).toString();
    return YYYYMMDD;
};

dateTimeFileName = function (time) {
    YYYYMMDDhhmm = time.getUTCFullYear().toString();
    YYYYMMDDhhmm += pad2(time.getUTCMonth() + 1).toString();
    YYYYMMDDhhmm += pad2(time.getUTCDate()).toString();
    YYYYMMDDhhmm += pad2(time.getUTCHours()).toString();
    YYYYMMDDhhmm += pad2(time.getUTCMinutes()).toString();
    return YYYYMMDDhhmm;
};

getForecastImageUrl = function(baseUrl, time) {
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/"));
    var initFileUrl = baseUrl.substring(baseUrl.lastIndexOf("/"), baseUrl.length - 16);
    var strTime = dateTimeFileName(new Date(time));
    url = beginUrl + initFileUrl + strTime + '.png';
    return url;
};

getDailyForecastImageUrl = function(baseUrl, time) {
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/"));
    var initFileUrl = baseUrl.substring(baseUrl.lastIndexOf("/"), baseUrl.length - 12);
    var strTime = dateFileName(new Date(time));
    url = beginUrl + initFileUrl + strTime + '.png';
    return url;
};

//***  Information sidebar drawer  ***//
// Based on articles on https://gomakethings.com

var drawer = function () {

  /**
  * Element.closest() polyfill
  * https://developer.mozilla.org/en-US/docs/Web/API/Element/closest#Polyfill
  */
  if (!Element.prototype.closest) {
    if (!Element.prototype.matches) {
      Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
    }
    Element.prototype.closest = function (s) {
      var el = this;
      var ancestor = this;
      if (!document.documentElement.contains(el)) return null;
      do {
        if (ancestor.matches(s)) return ancestor;
        ancestor = ancestor.parentElement;
      } while (ancestor !== null);
      return null;
    };
  }

  // Trap Focus
  // https://hiddedevries.nl/en/blog/2017-01-29-using-javascript-to-trap-focus-in-an-element
  //
  function trapFocus(element) {
    var focusableEls = element.querySelectorAll('a[href]:not([disabled]), button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled])');
    var firstFocusableEl = focusableEls[0];
    var lastFocusableEl = focusableEls[focusableEls.length - 1];
    var KEYCODE_TAB = 9;

    element.addEventListener('keydown', function(e) {
      var isTabPressed = (e.key === 'Tab' || e.keyCode === KEYCODE_TAB);

      if (!isTabPressed) {
        return;
      }

      if ( e.shiftKey ) /* shift + tab */ {
        if (document.activeElement === firstFocusableEl) {
          lastFocusableEl.focus();
            e.preventDefault();
          }
        } else /* tab */ {
        if (document.activeElement === lastFocusableEl) {
          firstFocusableEl.focus();
            e.preventDefault();
          }
        }
    });
  }

  //
  // Settings
  //
  var settings = {
    speedOpen: 50,
    speedClose: 350,
    activeClass: 'is-active',
    visibleClass: 'is-visible',
    selectorTarget: '[data-drawer-target]',
    selectorTrigger: '[data-drawer-trigger]',
    selectorClose: '[data-drawer-close]',

  };

  //
  // Methods
  //

  // Toggle accessibility
  var toggleAccessibility = function (event) {
    if (event.getAttribute('aria-expanded') === 'true') {
      event.setAttribute('aria-expanded', false);
    } else {
      event.setAttribute('aria-expanded', true);
    }
  };

  // Open Drawer
  var openDrawer = function (trigger) {

    // Find target
    var target = document.getElementById(trigger.getAttribute('aria-controls'));

    // Make it active
    target.classList.add(settings.activeClass);

    // Make body overflow hidden so it's not scrollable
    document.documentElement.style.overflow = 'hidden';

    // Toggle accessibility
    toggleAccessibility(trigger);

    // Make it visible
    setTimeout(function () {
      target.classList.add(settings.visibleClass);
      trapFocus(target);
    }, settings.speedOpen);

  };

  // Close Drawer
  var closeDrawer = function (event) {

    // Find target
    var closestParent = event.closest(settings.selectorTarget),
      childrenTrigger = document.querySelector('[aria-controls="' + closestParent.id + '"');

    // Make it not visible
    closestParent.classList.remove(settings.visibleClass);

    // Remove body overflow hidden
    document.documentElement.style.overflow = '';

    // Toggle accessibility
    toggleAccessibility(childrenTrigger);

    // Make it not active
    setTimeout(function () {
      closestParent.classList.remove(settings.activeClass);
    }, settings.speedClose);

  };

  // Click Handler
  var clickHandler = function (event) {

    // Find elements
    var toggle = event.target,
      open = toggle.closest(settings.selectorTrigger),
      close = toggle.closest(settings.selectorClose);

    // Open drawer when the open button is clicked
    if (open) {
      openDrawer(open);
    }

    // Close drawer when the close button (or overlay area) is clicked
    if (close) {
      closeDrawer(close);
    }

    // Prevent default link behavior
    if (open || close) {
      event.preventDefault();
    }

  };

  // Keydown Handler, handle Escape button
  var keydownHandler = function (event) {

    if (event.key === 'Escape' || event.keyCode === 27) {

      // Find all possible drawers
      var drawers = document.querySelectorAll(settings.selectorTarget),
        i;

      // Find active drawers and close them when escape is clicked
      for (i = 0; i < drawers.length; ++i) {
        if (drawers[i].classList.contains(settings.activeClass)) {
          closeDrawer(drawers[i]);
        }
      }

    }

  };

  //
  // Inits & Event Listeners
  //
  document.addEventListener('click', clickHandler, false);
  document.addEventListener('keydown', keydownHandler, false);

};

drawer();

// Scroll to element without adding anchor to URL
function smoothScrollTo(elementId) {
    var element = document.getElementById(elementId);
    element.scrollIntoView({
        block: 'start',
        behaviour: 'smooth'
    });
    return false;
}

// Current lat/lon/zoom utilities
function updateLatLonZoom(e, textBoxId) {
	var textBox = document.getElementById(textBoxId),
		newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    newUrl += "?lat=" + e.target.getCenter().lat.toFixed(3);
    newUrl += "&lon=" + e.target.getCenter().lng.toFixed(3);
    newUrl += "&zoom=" + e.target.getZoom();
    textBox.value = newUrl;
}
function copyToClipboard(textBoxId) {
    var textBox = document.getElementById(textBoxId);
    textBox.select();
    document.execCommand("copy");
}

// URL parameter functions
function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(n,key,value) {
        vars[key] = value;
    });
    return vars;
}
function getUrlParam(parameter, defaultvalue) {
    var urlparameter = defaultvalue;
    if(window.location.href.indexOf(parameter) > -1){
        urlparameter = getUrlVars()[parameter];
        }
    // TO DO check whether params are outside limits
    // such as forecastBounds, minZoom or maxZoom
    return urlparameter;
}
