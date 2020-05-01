"use strict";

// source: https://stackoverflow.com/a/10126042/8075455
const inactivityTime = () => {
    var time;
    window.addEventListener('load', resetTimer, true);
    add_active_events(resetTimer);

    function inactive() {
        location.replace("/idle-display");
    }

    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(inactive, 45000);
    }
}

window.addEventListener("load", inactivityTime);
