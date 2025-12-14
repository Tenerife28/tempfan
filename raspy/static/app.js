const VIB_CLICK = 15;
const VIB_TURBO = [70, 30, 150];
let lastVibrationVal = -1;

function updateSliderVal(val) {
    document.getElementById('sliderVal').innerText = val;
    if ((val == "0" || val == "50" || val == "100") && lastVibrationVal != val) {
        if (navigator.vibrate) navigator.vibrate(VIB_CLICK);
        lastVibrationVal = val;
    }
    else if (val != "0" && val != "50" && val != "100") {
        lastVibrationVal = -1;
    }
}

function triggerTurbo() {
    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ turbo: true })
    });


    if (navigator.vibrate) navigator.vibrate(VIB_TURBO);
}

function sendControl() {
    const isAuto = document.getElementById('autoToggle').checked;
    const speed = document.getElementById('speedSlider').value;

    document.getElementById('sliderContainer').style.opacity = isAuto ? "0.3" : "1";
    document.getElementById('speedSlider').disabled = isAuto;

    if (window.event && window.event.target.id === "autoToggle") {
        if (navigator.vibrate) navigator.vibrate(VIB_CLICK);
    }

    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            auto_mode: isAuto,
            speed: parseInt(speed)
        })
    });
}

function updateData() {
    fetch('/api/data')
        .then(r => r.json())
        .then(data => {
            document.getElementById('temp').innerText = data.temp + " °C";
            document.getElementById('rpm').innerText = data.rpm;

            if (data.mode === "TURBO") {
                document.getElementById('pwr').innerText = "🔥 TURBO 🔥";
                document.getElementById('pwr').style.color = "#e74c3c";
            } else {
                document.getElementById('pwr').innerText = data.speed_percent + " %";
                document.getElementById('pwr').style.color = "#3498db";
            }

            const toggle = document.getElementById('autoToggle');

            if (document.activeElement.id !== "speedSlider" && document.activeElement.id !== "autoToggle") {
                if (toggle.checked !== data.is_auto) {
                    toggle.checked = data.is_auto;
                    document.getElementById('sliderContainer').style.opacity = data.is_auto ? "0.3" : "1";
                    document.getElementById('speedSlider').disabled = data.is_auto;
                }

                if (!data.is_auto && document.activeElement.id !== "speedSlider") {
                    document.getElementById('speedSlider').value = data.manual_val * 100;
                    document.getElementById('sliderVal').innerText = Math.floor(data.manual_val * 100);
                }
            }
        })
        .finally(() => {
            setTimeout(updateData, 1000);
        });
}

updateData();