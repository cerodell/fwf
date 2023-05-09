(function($) {

  var options = {
    MIN_FRAME_DURATION: 50,   // ms
    MAX_FRAME_DURATION: 700,  // ms
    FRAME_DURATION_INCREMENT: 50, // ms
    defaultTZ: 'UTC',
    currentTZ: 'UTC',  // default from data
    currentTZName : 'UTC',
  };

  // Other timezone options can be added, but must be valid IANA
  // time zone database TZ names
  var timezoneOptions = [
    'UTC',
    'Canada/Pacific',
    'Canada/Mountain',
    'Canada/Central',
    'Canada/Eastern',
    'Canada/Atlantic',
    'Canada/Newfoundland',
  ];

  var zeroPad = function(n) {
    return n < 10 ? '0' + n : n;
  };

  var formatDate = function(date) {
    paddedDateElements = [
      date.year(),
      zeroPad(date.month() + 1),
      zeroPad(date.date()),
    ];
    return paddedDateElements.join('-') + ' ' + zeroPad(date.hour()) + ':' + zeroPad(date.minute());
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

  $.fn.slideshow = function(methodName) {
    var args = [].concat.apply([], arguments).slice(1);
    return this.each(function() {
      // Note that any defined methods will be called on all slideshow
      // instances at once
      if (methodName === 'jump2Image') {
        var imageNum = args[0];
        var imgPaths = $(this).data('imgPaths');
        var firstImg = $(this).data('firstImg');
        firstImg.attr('src', imgPaths[imageNum]);
      } else {
        // Create the slideshow (first call).
        // Initialization for individual slideshows and shared controls:
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

        // While images are loading, update the loading progress bar
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
      // Variables belonging to each .master multislideshow on
      // the page
      var imgNum = 0;
      var isPlaying = false;
      var shouldLoop = true;
      var frameDuration = 300; // ms
      var epochDates = [];
      var lastFrameTime = null;
      var timeoutID = null;
      var currentDatetime = null;

      // Find any slideshows inside this container and init them
      var slideshows = $(this).find('.slideshow').slideshow();

      // Get the dates from one of the slideshows
      slideshows.first().find('img').each(function() {
        epochDates.push($(this).data('date'));
      });
      var imgLen = epochDates.length;

      // Prepare datetime dropdown
      checkLocalStorage();
      initializeTimezoneDropdown();

      // Initialize range slider attributes
      var denomStr = '/' + imgLen;
      $('#ssRangeSlider').attr({
        "value": imgNum,
        "type": "range",
        "min": 0,
        "max": imgLen - 1,
        "step": 1,
        "title": (imgNum + 1) + denomStr,
      });

      // Bind event handlers to slideshow control buttons
      $('#firstImage').on('click', function() {
        if (isPlaying) {
          pause();
        }
        firstImage();
      });

      $('#prevImage').on('click', function() {
        if (isPlaying) {
          pause();
        }
        prevImage();
      });

      $('#togglePlay').on('click', function() {
        if (isPlaying) {
          pause();
        } else {
          play();
        }
      });

      $('#nextImage').on('click', function() {
        if (isPlaying) {
          pause();
        }
        nextImage();
      });

      $('#lastImage').on('click', function() {
        if (isPlaying) {
          pause();
        }
        lastImage();
      });

      $('#increaseSpeed').on('click', function() {
        changeFrameDuration(-options.FRAME_DURATION_INCREMENT);
      });

      $('#decreaseSpeed').on('click', function() {
        changeFrameDuration(options.FRAME_DURATION_INCREMENT);
      });

      $('#loop-continuous').on('click', function() {
        if ($(this).hasClass('active')) {
          $(this).removeClass('btn-primary').addClass('btn-default');
          $(this).attr('aria-pressed', 'false');
          shouldLoop = false;
        } else {
          $(this).removeClass('btn-default').addClass('btn-primary');
          $(this).attr('aria-pressed', 'true');
          shouldLoop = true;
        }
      });

      // Update current time for timezone change
      $('#timezone-options').on('change', function() {
        var selectedTZ = $(this).val();
        if (selectedTZ != options.currentTZ) {
          options.currentTZ = selectedTZ;
        }
        currentDatetime = currentDatetime.tz(options.currentTZ);
        $("#currenttime").html(formatDate(currentDatetime));
        updateLocalStorage();
      });

      // Add event listener to the range slider to enable click and drag
      // events to change displayed image
      $('#ssRangeSlider').on('input', function() {
        if (isPlaying) {
          pause();
        }
        jump2Image(parseInt($(this).val(), 10));
      });

      // Handle all aspects of image change events
      var jump2Image = function(n) {
        imgNum = n;
        slideshows.slideshow('jump2Image', n);
        updateCurrentTime(n);
        $("#ssRangeSlider").prop('value', n);
        $('#ssRangeSlider').prop('title', (n + 1) + denomStr);
        lastFrameTime = Date.now();
      };

      // Listen for triggered loaded events
      var numLoaded = 0;
      slideshows.on('loaded', function() {
        numLoaded++;
        if (numLoaded == slideshows.length) {
          $('html').addClass('imagesLoaded');
          $('#slideshow-controls button').prop('disabled', false);
          $('#ssRangeSlider').prop('disabled', false);
          firstImage(); // safety
          play();
        }
      });

      var pause = function() {
        isPlaying = false;
        $('#togglePlay span').removeClass('glyphicon-pause').addClass('glyphicon-play');
        $('#togglePlay').attr('title', 'Play');
        if (timeoutID != null) {
          clearTimeout(timeoutID);
          timeoutID = null;
        }
      }

      var play = function() {
        if (!isPlaying && imgNum === imgLen - 1) {
          firstImage();
        }
        isPlaying = true;
        $('#togglePlay span').removeClass('glyphicon-play').addClass('glyphicon-pause');
        $('#togglePlay').attr('title', 'Pause');
        timeoutID = setTimeout(stepWorld, frameDuration);
      }

      var stepWorld = function() {
        if (imgNum === imgLen - 2 && shouldLoop) {
          // Hold last frame longer when continuously looping
          t = 3 * frameDuration;
        } else {
          t = frameDuration;
        }
        if (imgNum === imgLen - 1) {
          if (shouldLoop) {
            jump2Image(0);
          } else {
            pause();
            return;
          }
        } else {
          nextImage();
        }
        timeoutID = setTimeout(stepWorld, t);
      }

      // Move to next image in slide show
      var nextImage = function() {
        if (imgNum === imgLen - 1) {
          jump2Image(0);
        } else {
          jump2Image(imgNum + 1);
        }
      };

      // Move to previous image in slide show
      var prevImage = function() {
        if (imgNum === 0) {
          jump2Image(imgLen - 1);
        } else {
          jump2Image(imgNum - 1);
        }
      };

      // Jump to first image in slideshow
      var firstImage = function() {
        jump2Image(0);
      };

      // Jump to last image in slideshow
      var lastImage = function() {
        jump2Image(imgLen - 1);
      };

      // Update current datetime content
      var updateCurrentTime = function(n) {
        var datetimeUTC = moment.tz(parseInt(epochDates[n], 10), options.defaultTZ);
        if (options.currentTZ != options.defaultTZ) {
          datetimeAware = datetimeUTC.tz(options.currentTZ);
        } else {
          datetimeAware = datetimeUTC;
        }
        currentDatetime = datetimeAware;
        formattedDateString = formatDate(datetimeAware);
        $("#currenttime").html(formattedDateString);
      }

      // Change frame duration time by `dv` ms.
      // If dv < 0, duration is increased
      // If dv > 0, duration is decreased
      var changeFrameDuration = function(dv) {
        frameDuration += dv;
        if (frameDuration > options.MAX_FRAME_DURATION) {
          frameDuration = options.MAX_FRAME_DURATION;
          $('#decreaseSpeed').prop('disabled', true);
        } else if (frameDuration < options.MIN_FRAME_DURATION) {
          frameDuration = options.MIN_FRAME_DURATION;
          $('#increaseSpeed').prop('disabled', true);
        } else {
          if ($('#play-mode-controls div:first-child button').is(':disabled')) {
            $('#play-mode-controls div:first-child button').prop('disabled', false);
          }
        }
        if (isPlaying) {
          // Handle if speed change occurs during a frame duration
          clearTimeout(timeoutID);
          timeoutID = null;
          var elapsedTime = Date.now() - lastFrameTime;
          if (elapsedTime >= frameDuration) {
            stepWorld();
          } else {
            timeoutID = setTimeout(stepWorld, frameDuration - elapsedTime);
          }
        }
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
