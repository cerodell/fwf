(function($) {
  // variable to replicate enumerated states
  var loopStates = {
    LOOP_CONTINUOUS: 0,
    LOOP_ONCE: 1,
  };

  // 'Module' variables
  var options = {
    imgNum: 0,
    imgLen: 0,
    epochDates: [],
    loopSpeed: 300, // ms
    loopInterval: null,    // The variable responsible for set and clearInterval()
    currentlyLooping: false,  // true if currently looping, false otherwise
    loopFwd: true,    // true if looping fwd, false if in reverse
    loopType: loopStates.LOOP_CONTINUOUS,
    speedChange: false,  // A debouncer to smoothen the effect of changing loop speed mid loop
    MAX_LOOP_SPEED: 50,
    MIN_LOOP_SPEED: 900,
    currentDatetime: null,
    defaultTZ: 'UTC',
    currentTZ: 'UTC',  // default from data
    currentTZName : 'UTC',
  };

  var timezoneOptions = [
    'UTC', // UTC
    'Canada/Pacific', // Pacific
    'Canada/Mountain', // Mountain
    'Canada/Central', // Central
    'Canada/Eastern', // Eastern
    'Canada/Atlantic', // Atlantic
    'Canada/Newfoundland', // Newfoundland
  ];

  var pad = function(n) {
    return n < 10 ? '0' + n : n;
  };

  var formatdate = function(date) {
    paddedDateElements = [
      date.year(),
      pad(date.month() + 1),
      pad(date.date()),
    ];
    return paddedDateElements.join('-') + ' ' + pad(date.hour()) + ':' + pad(date.minute());
  };

  var initializeTimezoneDropdown = function() {
    var tzAbbrs = [];
    for (i in timezoneOptions) {
      tzAbbrs.push(moment(new Date()).tz(timezoneOptions[i]).zoneAbbr());
    }
    options.tzOptions = tzAbbrs;
    var tzHTMLTags = '';
    for (i in tzAbbrs) {
      tzHTMLTags += '<option ' +
        (options.currentTZ === timezoneOptions[i]? 'selected="selected"': '') +
        ' value="' +
        moment.tz.zone(timezoneOptions[i]).name +
        '">'+
        options.tzOptions[i] +
        '</option>';
    }
    $('#timezone-options').html(tzHTMLTags);
  };

  var checkLocalStorage = function() {
    options.currentTZ = options.defaultTZ;
    if (typeof(Storage) !== "undefined") {
      if (localStorage.getItem('timeZone') !== null) {
        options.currentTZ = localStorage.getItem('timeZone');
      }
    }
  };

  var updateLocalStorage = function() {
    if (typeof(Storage) !== "undefined") {
      localStorage.setItem('timeZone', options.currentTZ);
    }
  };

  // Update current time for timezone change
  $('#timezone-options').on('change', function() {
    var selectedTZ = $(this).val();
    if (selectedTZ != options.currentTZ) {
      options.currentTZ = selectedTZ;
    }
    options.currentDatetime = options.currentDatetime.tz(options.currentTZ);
    $("#currenttime").html(formatdate(options.currentDatetime));
    updateLocalStorage();
  })

  $('#loop-continuous').on('click', function() {
    if ($(this).hasClass('active')) {
      $(this).removeClass('btn-primary').addClass('btn-default');
      $(this).attr('aria-pressed', 'false');
    } else {
      $(this).removeClass('btn-default').addClass('btn-primary');
      $(this).attr('aria-pressed', 'true');
    }
  });

  $.fn.slideshow = function(methodName) {
    var args = [].concat.apply([], arguments).slice(1);
    return this.each(function() {
      if (methodName === 'jump2Image') {
        var imageNum = args[0];
        var imgPaths = $(this).data('imgPaths');
        var firstImg = $(this).data('firstImg');
        if (options.imgNum > options.imgLen) {
          options.imgNum = options.imgLen;
        } else if (options.imgNum < 0) {
          options.imgNum = 0;
        }
        firstImg.attr('src', imgPaths[imageNum]);
      } else {
        // slideshow is called for the first time.
        // Initialize for individual slideshows and/or shared controls
        var imgPaths = [];
        $(this).find('img').each(function() {
          imgPaths.push(this.src);
        });
        $(this).data('imgPaths', imgPaths);
        $(this).data('firstImg', $(this).find('img').first());

        // Initialize progress bar attributes
        $(this).find('.progress-bar').attr({
          'aria-valuemax': imgPaths.length,
          'aria-valuemin': 0,
          'aria-valuenow': imgPaths.length,
        });

        var handleImagesLoaded = function(images) {
          $(this).find('.loading-indicator').remove();
          $(this).trigger('loaded');
        }.bind(this);

        var handleImagesLoading = function(i, n) {
          var percentage = (i/n)*100;
          $(this).find('.progress-bar')
            .removeClass('active')
            .removeClass('progress-bar-striped')
            .css('width', percentage+'%')
            .attr('aria-valuenow', i);
        }.bind(this);

        // Preload images
        setTimeout(function() {
          preloadImages(
            imgPaths,
            handleImagesLoaded,
            handleImagesLoading
          );
        }, 0);

        // return the slideshow itself
        return this;
      }
    });
  };
  $.fn.multiSlideshow = function() {
    return this.each(function() {

      // Find any slideshows inside this container and init them
      var slideshows = $(this).find('.slideshow').slideshow();

      // Get the dates from one of the slideshows
      slideshows.first().find('img').each(function() {
        options.epochDates.push($(this).data('date'));
      });
      options.imgNum = 0;
      options.imgLen = options.epochDates.length-1;

      // Prepare datetime dropdown
      checkLocalStorage();
      initializeTimezoneDropdown();

      // Initialize the range slider
      $('#ssRangeSlider').attr({
        "value": options.imgNum,
        "type": "range",
        "id": "ssRangeSlider",
        "min": 0,
        "max": options.imgLen,
        "step": 1,
        "title": String(options.imgNum) + '/' + String(options.imgLen),
      });

      // Bind event handlers to slideshow control buttons
      $('#firstImage').on('click', function() {
        firstImage();
      });

      $('#prevImage').on('click', function() {
        prevImage();
      });

      $('#autoLoop').on('click', function() {
        autoLoop();
      });

      $('#nextImage').on('click', function() {
        nextImage();
      });

      $('#lastImage').on('click', function() {
        lastImage();
      });

      $('#increaseSpeed').on('click', function() {
        increaseSpeed();
      });

      $('#decreaseSpeed').on('click', function() {
        decreaseSpeed();
      });

      $('#ssOnce').on('click', function() {
        checkLoopState();
      });

      var radioLoop = $('#ssLoop');
      radioLoop.on('click', function() {
        checkLoopState();
      });

      // Add event listener to the range slider to enable click and drag
      // events to change displayed image
      $('#ssRangeSlider').on('input', function() {
        jump2Image($(this).val());
      });

      // Now slideshows is a reference to all individual slideshows.
      // Any defined 'method' can be called on all of them at once
      var jump2Image = function(n) {
        slideshows.slideshow('jump2Image', n);
        updateCurrentTime()
      };

      // Listen for triggered loaded events
      var numLoaded = 0;
      slideshows.on('loaded', function() {
        numLoaded++;
        if (numLoaded == slideshows.length) {
          $('html').addClass('imagesLoaded');
          $('#slideshow-controls button').prop('disabled', false);
          $('#ssRangeSlider').prop('disabled', false);
          firstImage(); // needed?
          autoLoop();
        }
      });

      var checkLoopState = function() {
        if ($('#ssOnce').is(':checked')) {
          options.loopFwd = true;
          options.loopType = loopStates.LOOP_ONCE;
        } else if ($('#ssLoop').is(':checked')) {
          options.loopFwd = true;
          options.loopType = loopStates.LOOP_CONTINUOUS;
        }
      };

      var autoLoop = function() {
        if (options.currentlyLooping) {
          // If currently looping, turn it off
          clearLoopInterval();
        } else {
          // If not currently looping, turn it on
          options.currentlyLooping = true;
          $('#autoLoop span').removeClass('glyphicon-play').addClass('glyphicon-pause');
          if (options.imgNum >= options.imgLen && options.loopType == loopStates.LOOP_ONCE) {
            // must be -1, beacuse this gets incremented in changeImage
            options.imgNum = -1;
          }
          autoLoopFwd();
        }
      };

      // Automatically Loop forward through the images
      var autoLoopFwd = function() {
        options.loopFwd = true;
        options.loopInterval = setInterval( function() { changeImage(1); }, options.loopSpeed);
      }

      // Automatically loops through images in reverse
      // This was initially written to provide functionality
      // to the loop-relect option, however, this options is
      // currently not implemented
      var autoLoopRev = function() {
        options.loopRev = false;
        options.loopInterval = setInterval( function() { changeImage(-1); }, options.loopSpeed);
      };

      // Move forward or back an image
      // param: direction
      //           the direction to move, must be either 1 (forward) or
      //           0 (backwards)
      var changeImage = function(direction) {

        // If the speed has been changed while in the middle of a loops
        // make sure that it turns off the debouncer and continues on with
        // the new speed
        if (options.speedChange) {
          options.speedChange = false;
          clearLoopInterval();
          if (direction > 0) {
            autoLoopFwd();
          } else if (direction < 0 ) {
            autoLoopRev();
          }
        }

        options.imgNum += parseInt(direction, 10);

        if (options.loopType == loopStates.LOOP_ONCE) {
          if (options.imgNum > options.imgLen && options.currentlyLooping) {
            options.imgNum = options.imgLen;
            clearLoopInterval();
          } else if (options.imgNum > options.imgLen) {
            options.imgNum = 0;
          }
        }
        else if (options.loopType == loopStates.LOOP_CONTINUOUS) {
          if (options.imgNum > options.imgLen) {
            options.imgNum = 0;
          } else if (options.imgNum < 0) {
            options.imgNum = options.imgLen;
          }
        }

        $("#ssRangeSlider").prop('value', options.imgNum);
        jump2Image(options.imgNum);

      };

      // Move to next image in slide show.  If the slideshow is automatically
      // looping then first stop the loop and then move forward one image
      var nextImage = function() {
        if (options.currentlyLooping) {
          clearLoopInterval();
        }
        changeImage(1);
      };

      // Move to previous image in slide show.  If the slideshow is automatically
      // looping then first stop the loop and then move back one image
      var prevImage = function() {
        if (options.currentlyLooping) {
          clearLoopInterval();
        }
        changeImage(-1);
      };

      // Jump to first image in slideshow.  If the slideshow is automatically
      // looping then first stop the loop and then move back one image
      var firstImage = function() {
        if (options.currentlyLooping) {
          clearLoopInterval();
        }
        options.imgNum = 0;
        $("#ssRangeSlider").prop('value', options.imgNum);
        jump2Image(options.imgNum);
      };

      // Jump to last image in slideshow. If the slideshow is automatically
      // looping then first stop the loop and then move back one image
      var lastImage = function() {
        if (options.currentlyLooping) {
          clearLoopInterval();
        }
        options.imgNum = options.imgLen;
        $("#ssRangeSlider").prop('value', options.imgNum);
        jump2Image(options.imgNum);
      };

      // Update current date content
      var updateCurrentTime = function() {
        var datetimeUTC = moment.tz(parseInt(options.epochDates[options.imgNum], 10), "UTC");
        if (options.currentTZ != options.defaultTZ) {
          datetimeAware = datetimeUTC.tz(options.currentTZ);
        } else {
          datetimeAware = datetimeUTC;
        }
        options.currentDatetime = datetimeAware;
        formattedDateString = formatdate(datetimeAware);
        $("#currenttime").html(formattedDateString);
      }

      // Increases loop speed by shortening time interval by 50 ms
      var increaseSpeed = function() {
        if (options.currentlyLooping) {
          options.speedChange = true;
        }
        changeSpeed(-50);
      };

      // Decreases loop speed by lengthening time interval by 50ms
      var decreaseSpeed = function() {
        if (options.currentlyLooping) {
          options.speedChange = true;
        }
        changeSpeed(50);
      };

      // Changes loop speed
      // param: dv
      //      the change in speed, if dv < 0, then speed is increasing and
      //      if dv > 0 then speed is decreasing
      var changeSpeed = function(dv) {
        options.loopSpeed += parseInt(dv, 10);
        if (options.loopSpeed < options.MAX_LOOP_SPEED) {
          options.loopSpeed = options.MAX_LOOP_SPEED;
        } else if (options.loopSpeed > options.MIN_LOOP_SPEED) {
          options.loopSpeed = options.MIN_LOOP_SPEED;
        }
      };

      var clearLoopInterval = function() {
        options.currentlyLooping = false;
        $('#autoLoop span').removeClass('glyphicon-pause').addClass('glyphicon-play');
        window.clearInterval(options.loopInterval);
      };

    });
  };

  $(document).ready(function() {
    $('.master').multiSlideshow();
  });
})(jQuery);

/* Preload images modified from Eike Send's code:
 *
 * Copyright (C) 2012 Eike Send
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */
function preloadImages(imgUrls, callback, iterativecallback) {
  "use strict";
  var images = [];
  var numLoaded = 0;
  imgUrls = Object.prototype.toString.call(imgUrls) === '[object Array]'
  ? imgUrls
  : [imgUrls];
  var handleLoad = function() {
  numLoaded++;
  // Some browsers fire onload events whenever an animated
  // GIF restarts a loop, so remove the on* handlers now.
  this.onabort = this.onerror = this.onload = null;
  if (iterativecallback) {
    iterativecallback(numLoaded, imgUrls.length);
  }
  if (callback && numLoaded === imgUrls.length) {
    callback(images);
  }
  };
  var image;
  for (var i = 0; i < imgUrls.length; i++) {
  image = images[i] = new Image();
  image.onabort = image.onerror = image.onload = handleLoad;
  image.src = imgUrls[i];
  if (image.complete) {
    // Image is likely cached. Fire the handler right away.
    image.onabort = image.onerror = image.onload = null;
    handleLoad.call(image);
  }
  }
}
