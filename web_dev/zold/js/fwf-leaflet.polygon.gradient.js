(function (factory, window) {

    // define an AMD module that relies on 'leaflet'
    if (typeof define === 'function' && define.amd) {
        define(['leaflet'], factory);

        // define a Common JS module that relies on 'leaflet'
    } else if (typeof exports === 'object') {
        module.exports = factory(require('leaflet'));
    }

    // attach your plugin to the global 'L' letiable
    if (typeof window !== 'undefined' && window.L) {
        window.L.ArrowPath = factory(L);
    }
}(function (L) {

    L.SVG.include({
        _updateStyle: function (layer) {

            let path = layer._path,
                options = layer.options;

            if (!path) {
                return;
            }

            if (options.stroke) {
                path.setAttribute('stroke', options.color);
                path.setAttribute('stroke-opacity', options.opacity);
                path.setAttribute('stroke-width', options.weight);
                path.setAttribute('stroke-linecap', options.lineCap);
                path.setAttribute('stroke-linejoin', options.lineJoin);

                if (options.dashArray) {
                    path.setAttribute('stroke-dasharray', options.dashArray);
                } else {
                    path.removeAttribute('stroke-dasharray');
                }

                if (options.dashOffset) {
                    path.setAttribute('stroke-dashoffset', options.dashOffset);
                } else {
                    path.removeAttribute('stroke-dashoffset');
                }
            } else {
                path.setAttribute('stroke', 'none');
            }

            if (options.fill) {
                this._polyFill(layer, path, options);
                path.setAttribute('fill-opacity', options.fillOpacity);
                path.setAttribute('fill-rule', options.fillRule || 'evenodd');
            } else {
                path.setAttribute('fill', 'none');
            }
        },
        _polyFill(layer, path, options) {
            let fillColor = options.fillColor;
            let isLinearGradient = fillColor.match(/^linearGradient\(/);
            let isRadialGradient = fillColor.match(/^radialGradient\(/);

            if (fillColor.match(/^#/)) {
                path.setAttribute('fill', fillColor || options.color);
            } else if (isLinearGradient || isRadialGradient) {
                let gradientOpt = this._addGradient(fillColor);
                if (isLinearGradient) {
                    this._addLinearGradient(layer, gradientOpt);
                } else {
                    this._addRadialGradient(layer, gradientOpt);
                }
            } else if (fillColor.match(/^url\(/)) {
                this._fillByImage(layer);
            }
        },
        _addLinearGradient: function (layer, gradientOpt) {
            let path = layer._path;
            let colorStr = layer.options.fillColor;
            let gradientId = 'gradient' + gradientOpt.index;

            this._addDefs();

            if (!gradientOpt.exist) {
                let gradient = L.SVG.create('linearGradient');
                gradient.setAttribute('id', gradientId);

                let arrMap = this._getLinearProperties(colorStr, ['linearGradient(', ')']);
                this._addStops(gradient, arrMap);

                this._addAngle(gradient, arrMap.angle);

                this._defs.appendChild(gradient);
            }

            path.setAttribute('fill', 'url(#' + gradientId + ')');
        },
        _addRadialGradient: function (layer, gradientOpt) {
            let path = layer._path;
            let colorStr = layer.options.fillColor;
            let gradientId = 'gradient' + gradientOpt.index;

            this._addDefs();

            if (!gradientOpt.exist) {
                let gradient = L.SVG.create('radialGradient');
                gradient.setAttribute('id', gradientId);

                let arrMap = this._getRadialProperties(colorStr, ['radialGradient(', ')']);
                this._addStops(gradient, arrMap);

                this._addAttribute(gradient, arrMap);
                //
                this._defs.appendChild(gradient);
            }

            path.setAttribute('fill', 'url(#' + gradientId + ')');
        },
        _addAttribute(gradient, arr) {
            gradient.setAttribute('cx', arr.cx);
            gradient.setAttribute('cy', arr.cy);
            gradient.setAttribute('r', arr.r);
            gradient.setAttribute('fx', arr.fx);
            gradient.setAttribute('fy', arr.fy);
        },

        _getRadialProperties(colorStr, replaceArr) {
            let string = colorStr;
            for (let i = 0, l = replaceArr.length; i < l; i ++) {
                let str = replaceArr[i];
                string = string.replace(str, '');
            }
            let arrays = string.split(/[\,]+/);
            let colorArr = arrays.slice(5);
            let resColors = [];
            let resOffsets = [];
            let offsetNum = 0;
            for (let i = 0, l = colorArr.length; i < l; i ++) {
                let str = colorArr[i];
                let opts = str.trim().split(/\s+/);
                resColors.push(opts[0]);
                if(opts.length > 1 || i === l - 1) {
                    let offset;
                    if(opts.length > 1) {
                        offset = parseFloat(opts[1]);
                    } else {
                        offset = 100;
                    }

                    let len = resOffsets.length;
                    if(offsetNum > 0) {
                        let startNum = len - offsetNum - 1;
                        let startVal = parseFloat(resOffsets[startNum]);
                        let step = (offset - startVal) / (offsetNum + 1);
                        for (let j = 1; j <= offsetNum; j ++) {
                            resOffsets[startNum + j] = startVal + step * j + '%';
                        }
                        offsetNum = 0;
                    }
                    resOffsets.push(offset + '%');
                } else {
                    if(i !== 0) {
                        offsetNum = offsetNum + 1;
                        resOffsets.push('');
                    } else {
                        resOffsets.push('0%');
                    }
                }
            }
            return {
                cx: arrays[0].trim(),
                cy: arrays[1].trim(),
                r: arrays[2].trim(),
                fx: arrays[3].trim(),
                fy: arrays[4].trim(),
                colors: resColors,
                offsets: resOffsets
            }
        },
        _addGradient(gradient) {
            if (!this._gradientArray) {
                this._gradientArray = [];
            }
            let gradientStr = gradient.split(/[\s\,\-\(\)]+/).join('');
            let index = this._gradientArray.indexOf(gradientStr);
            if (index > -1) {
                return {index: index, exist: true}
            }
            this._gradientArray.push(gradientStr);
            return {index: this._gradientArray.length - 1, exist: false}
        },
        _addDefs() {
            if (!this._defs) {
                this._defs = L.SVG.create('defs');
                this._container.appendChild(this._defs);
            }
        },
        _addAngle(gradient, angle) {
            gradient.setAttribute('x1', '0');
            gradient.setAttribute('y1', '0');
            gradient.setAttribute('x2', '1');
            gradient.setAttribute('y2', '0');
            gradient.setAttribute('gradientTransform', 'rotate('+angle.replace('deg', '')+')');
        },
        _addStops(gradient, options) {
            let colors = options.colors;
            let offsets = options.offsets;
            for (let i = 0, len = colors.length; i < len; i++) {
                let stop = L.SVG.create('stop');
                stop.setAttribute('offset', offsets[i]);
                stop.setAttribute('stop-color', colors[i]);
                gradient.appendChild(stop);
            }
        },
        _getLinearProperties(colorStr, replaceArr) {
            let string = colorStr;
            for (let i = 0, l = replaceArr.length; i < l; i ++) {
                let str = replaceArr[i];
                string = string.replace(str, '');
            }
            let arrays = string.split(/[\,]+/);
            let colorArr = arrays.slice(1);
            let resAngle = arrays[0].trim();
            let resColors = [];
            let resOffsets = [];
            let offsetNum = 0;
            for (let i = 0, l = colorArr.length; i < l; i ++) {
                let str = colorArr[i];
                let opts = str.trim().split(/\s+/);
                resColors.push(opts[0]);
                if(opts.length > 1 || i === l - 1) {
                    let offset;
                    if(opts.length > 1) {
                        offset = parseFloat(opts[1]);
                    } else {
                        offset = 100;
                    }

                    let len = resOffsets.length;
                    if(offsetNum > 0) {
                        let startNum = len - offsetNum - 1;
                        let startVal = parseFloat(resOffsets[startNum]);
                        let step = (offset - startVal) / (offsetNum + 1);
                        for (let j = 1; j <= offsetNum; j ++) {
                            resOffsets[startNum + j] = startVal + step * j + '%';
                        }
                        offsetNum = 0;
                    }
                    resOffsets.push(offset + '%');
                } else {
                    if(i !== 0) {
                        offsetNum = offsetNum + 1;
                        resOffsets.push('');
                    } else {
                        resOffsets.push('0%');
                    }
                }
            }
            return {
                angle: resAngle,
                colors: resColors,
                offsets: resOffsets
            }
        },

        //借鉴自插件leaflet-polygon-fillPattern
        _fillByImage: function (layer) {
            let path = layer._path,
                options = layer.options,
                fill = options.fillColor;
            this._addDefs();

            let _img_url = fill.replace(/url\(+/, '').replace(/\)+/, '');/*.substring(4, fill.length - 1)*/
            let _refOption = this._addRefId(_img_url);
            let _ref_id = _img_url + _refOption.index;
            if (!_refOption.exist) {
                this._addPattern(_img_url, _ref_id, options);
            }
            path.setAttribute('fill', "url(#" + _ref_id + ")");
        },
        _addRefId(url) {
            if (!this._imgUrls) {
                this._imgUrls = [];
            }
            let index = this._imgUrls.indexOf(url);
            if (index > -1) {
                return {index: index, exist: true}
            }
            this._imgUrls.push(url);
            return {index: this._imgUrls.length - 1, exist: false}
        },
        _addPattern(_img_url, _ref_id, options) {
            let _im = new Image();
            _im.src = _img_url;

            let _p = L.SVG.create('pattern');
            _p.setAttribute('id', _ref_id);
            _p.setAttribute('x', '0');
            _p.setAttribute('y', '0');
            _p.setAttribute('patternUnits', 'userSpaceOnUse');
            _p.setAttribute('width', '24');
            _p.setAttribute('height', '24');

            let _rect = L.SVG.create('rect');
            _rect.setAttribute('width', 24);
            _rect.setAttribute('height', 24);
            _rect.setAttribute('x', 0);
            _rect.setAttribute('x', 0);
            _rect.setAttribute('fill', options.fillColor || options.color);

            let _img = L.SVG.create('image');
            _img.setAttribute('x', '0');
            _img.setAttribute('y', '0');
            _img.setAttributeNS('http://www.w3.org/1999/xlink', 'href', _img_url);
            _img.setAttribute('width', '24');
            _img.setAttribute('height', '24');

            _p.appendChild(_rect);
            _p.appendChild(_img);

            this._defs.appendChild(_p);

            _im.onload = function () {
                _p.setAttribute('width', _im.width);
                _p.setAttribute('height', _im.height);
                _img.setAttribute('width', _im.width);
                _img.setAttribute('height', _im.height);
            };
        }

    })

}, window));
