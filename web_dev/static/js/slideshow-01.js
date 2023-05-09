(function($) {

    // variable to replicate enumerated states
    var loopStates = {
        LOOP_CONTINUOUS: 0,
        LOOP_ONCE: 1,
        LOOP_REFLECT: 2,
    };

    // 'Modlue' variables
    var options = {
        imgNum: 0,
        imgLen: 0,
        allImages: new Array(),
        epochDates: [],
        loopSpeed: 300, // ms
        loopInterval: null,      // The variable responsible for set and clearInterval()
        currentlyLooping: false,    // true if currently looping, false otherwise
        loopFwd: true,      // true if looping fwd, false if in reverse
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
            tzHTMLTags += '<option '+ (options.currentTZ === timezoneOptions[i]? 'selected="selected"': '') +' value="' + moment.tz.zone(timezoneOptions[i]).name + '">'+ options.tzOptions[i] + '</option>';
        }
        document.getElementById('timezone-options').innerHTML = tzHTMLTags;
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
        document.querySelector("#currenttime").innerHTML = formatdate(options.currentDatetime);
        updateLocalStorage();
    })

    // The constructor for this plugin.  It will set all the default variables
    // and take care of any initialization needed to run the slideshow
    $.fn.slideShow = function() {
        return this.each(function() {

            // Get Number of images in slideshow
            var images = this.getElementsByTagName('img');
            // Remove any tags that aren't images
            $(this.children).not('img').remove();

            for (var i = images.length-1; i >= 0; i--) {
                var tmpImg = images[i].src;
                options.allImages.unshift(tmpImg);
                options.epochDates.unshift($(images[i]).data('date'));
                if (i != 0) {
                    images[i].parentNode.removeChild(images[i]);
                }
            }
            options.imgNum = 0;
            options.imgLen = options.allImages.length-1;

            // Prepare datetime dropdown
            checkLocalStorage();
            initializeTimezoneDropdown();

            // Display control buttons
            var ssControls = document.getElementById('slideshow-controls');
            ssControls.style.display = 'block';

            // Initialize the range slider
            var rangeSlider = document.createElement('Input');
            var attrs = {
                "value": options.imgNum,
                "type":"range",
                "id":"ssRangeSlider",
                "min":0,
                "max":options.imgLen,
                "step":0,
                "title": String(options.imgNum) + '/' + String(options.imgLen),
            };

            for (var key in attrs) {
                rangeSlider.setAttribute(key, attrs[key]);
            }
            var ssControls = document.getElementById('slideshow-controls');
            ssControls.insertBefore(rangeSlider, ssControls.firstChild);

            // Bind event handlers to slideshow control buttons
            var firstImage = $('#firstImage');
            firstImage.on('click', function() {
                $(this).firstImage();
            });

            var pImage = $('#prevImage');
            pImage.on('click', function() {
                $(this).prevImage();
            });

            var autoLoop = $('#autoLoop');
            autoLoop.on('click', function(){
                $(this).auto();
            });

            var nImage = $('#nextImage');
            nImage.on('click', function() {
                $(this).nextImage();
            });

            var lastImage = $('#lastImage');
            lastImage.on('click', function() {
                $(this).lastImage();
            });

            var increaseSpeed = $('#increaseSpeed');
            increaseSpeed.on('click', function() {
                $(this).increaseSpeed();
            });

            var decreaseSpeed = $('#decreaseSpeed');
            decreaseSpeed.on('click', function() {
                $(this).decreaseSpeed();
            });

            var radioOnce = $('#ssOnce');
            radioOnce.on('click', function() {
                $(this).checkLoopState();
            });

            // Not currently implemented
            // var radioReflect = $('#ssReflect');
            // radioReflect.on('click', function() {
            //     $(this).checkLoopState();
            // });

            var radioLoop = $('#ssLoop');
            radioLoop.on('click', function() {
                $(this).checkLoopState();
            });

            // Add event listener to the range slider to enable click and drag
            // events to change displayed image
            var rangeInput = document.getElementById("ssRangeSlider");
            if (rangeInput.addEventListener) {
                rangeInput.addEventListener("input", function() {
                    var next = parseInt(rangeInput.value);
                    $(this).jump2Image(next);
                }, false);
            } else if (rangeInput.attachEvent) {
                rangeInput.attachEvent('change', function() {
                    var next = parseInt(rangeInput.value);
                    $(this).jump2Image(next);
                });
            }

            // update for first time
            $(this).firstImage();
        });
    };

    $.fn.checkLoopState = function() {
        if ( document.getElementById('ssOnce').checked ) {
            options.loopFwd = true;
            options.loopType = loopStates.LOOP_ONCE;
        } else if (document.getElementById('ssLoop').checked){
            options.loopFwd = true;
            options.loopType = loopStates.LOOP_CONTINUOUS;
        }
        // reflect not implemented as of yet
        else if ( document.getElementById('ssReflect').checked ) {
            options.loopType = loopStates.LOOP_REFLECT;
        }
    };

    $.fn.auto = function() {
        // If currently looping, turn it off
        if (options.currentlyLooping) {
            this.clearLoopInterval();
        }
        // If not currently looping, turn it on
        else  {
            options.currentlyLooping = true;
            $(document.getElementById('autoLoop').getElementsByTagName('span')[0]).removeClass('glyphicon-play').addClass('glyphicon-pause');
            if (options.imgNum >= options.imgLen && options.loopType == loopStates.LOOP_ONCE) {
                // must be -1, beacuse this gets incremented in changeImage
                options.imgNum = -1;
            }
            this.autoLoopFwd();
        }
    };

    // Automatically Loop forward through the images
    $.fn.autoLoopFwd = function() {
        options.loopFwd = true;
        options.loopInterval = setInterval( function() { $(this).changeImage(1); }, options.loopSpeed);
    }

    // Automatically loops through images in reverse
    // This was initially written to provide functionality
    // to the loop-relect option, however, this options is
    // currently not implemented
    $.fn.autoLoopRev = function() {
        options.loopRev = false;
        options.loopInterval = setInterval( function() { $(this).changeImage(-1); }, options.loopSpeed);
    };

    // Move forward or back an image
    // param: direction
    //                 the direction to move, must be either 1 (forward) or
    //                 0 (backwards)
    $.fn.changeImage = function(direction) {

        // If the speed has been changed while in the middle of a loops
        // make sure that it turns off the debouncer and continues on with
        // the new speed
        if (options.speedChange) {
            options.speedChange = false;
            this.clearLoopInterval();
            if (direction > 0) {
                this.autoLoopFwd();
            } else if (direction < 0 ) {
                this.autoLoopRev();
            }
        }

        var nextImage = options.imgNum + parseInt(direction);
        options.imgNum += parseInt(direction);

        if (options.loopType == loopStates.LOOP_ONCE) {
            if (options.imgNum > options.imgLen && options.currentlyLooping) {
                options.imgNum = options.imgLen;
                this.clearLoopInterval();
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

        document.getElementById("ssRangeSlider").value = options.imgNum;

        $.fn.jump2Image(options.imgNum);

    };

    // Move to next image in slide show.  If the slideshow is automatically
    // looping then first stop the loop and then move forward one image
    $.fn.nextImage = function() {
        if (options.currentlyLooping) {
            this.clearLoopInterval();
        }
        this.changeImage(1);
    };

    // Move to previous image in slide show.  If the slideshow is automatically
    // looping then first stop the loop and then move back one image
    $.fn.prevImage = function() {
        if (options.currentlyLooping) {
            this.clearLoopInterval();
        }
        this.changeImage(-1);
    };

    // Jump to first image in slideshow.  If the slideshow is automatically
    // looping then first stop the loop and then move back one image
    $.fn.firstImage = function() {
        if (options.currentlyLooping) {
            this.clearLoopInterval();
        }
        options.imgNum = 0;
        document.getElementById("ssRangeSlider").value = options.imgNum;
        this.jump2Image( options.imgNum );
    };

    // Jump to last image in slideshow. If the slideshow is automatically
    // looping then first stop the loop and then move back one image
    $.fn.lastImage = function() {
        if (options.currentlyLooping) {
            this.clearLoopInterval();
        }
        options.imgNum = options.imgLen;
        document.getElementById("ssRangeSlider").value = options.imgNum;
        this.jump2Image(options.imgNum);
    };

    // Move to specified image, given by imgNum in slideshow
    // param: img
    //           the image number to jump to, must be between 0 and
    //           numImages - 1
    $.fn.jump2Image = function(num) {
        if (num > options.imgLen) {
            num = options.imgLen;
        } else if (num < 0) {
            num = 0;
        }
        options.imgNum = num;
        var imgSrc = options.allImages[options.imgNum];
        document.querySelector("#slideshow img").src = imgSrc;

        // Update current date content
        var datetimeUTC = moment.tz(parseInt(options.epochDates[options.imgNum], 10), "UTC");
        if (options.currentTZ != options.defaultTZ) {
            datetimeAware = datetimeUTC.tz(options.currentTZ);
        } else {
            datetimeAware = datetimeUTC;
        }
        options.currentDatetime = datetimeAware;
        formattedDateString = formatdate(datetimeAware);
        document.querySelector("#currenttime").innerHTML = formattedDateString;
    }

    // Increases loop speed by shortening time interval by 50 ms
    $.fn.increaseSpeed = function() {
        if (options.currentlyLooping) {
            options.speedChange = true;
        }
        this.changeSpeed(-50);
    };

    // Decreases loop speed by lengthening time interval by 50ms
    $.fn.decreaseSpeed = function() {
        if (options.currentlyLooping) {
            options.speedChange = true;
        }
        this.changeSpeed(50);
    };

    // Changes loop speed
    // param: dv
    //          the change in speed, if dv < 0, then speed is increasing and
    //          if dv > 0 then speed is decreasing
    $.fn.changeSpeed = function( dv ) {
        options.loopSpeed += parseInt(dv);
        if (options.loopSpeed < options.MAX_LOOP_SPEED) {
            options.loopSpeed = options.MAX_LOOP_SPEED;
        } else if (options.loopSpeed > options.MIN_LOOP_SPEED) {
            options.loopSpeed = options.MIN_LOOP_SPEED;
        }
    };

    $.fn.clearLoopInterval = function() {
        options.currentlyLooping = false;
        $(document.getElementById('autoLoop').getElementsByTagName('span')[0]).removeClass('glyphicon-pause').addClass('glyphicon-play');
        window.clearInterval(options.loopInterval);
    }

    $.fn.getOptions = function() {
        return options;
    }

}(jQuery));

$('#slideshow').slideShow();
