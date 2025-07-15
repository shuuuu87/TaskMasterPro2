// race_result_modal.js
// Polls for race result and shows modal if race ended
function pollRaceResult() {
    fetch('/race/result_status')
        .then(response => response.json())
        .then(data => {
            if (data.show_modal) {
                showRaceResultModal(data);
            }
        });
}

function showRaceResultModal(data) {
    if (document.getElementById('race-result-modal')) return;
    const modal = document.createElement('div');
    modal.id = 'race-result-modal';
    modal.innerHTML = `
        <div class="race-modal-overlay"></div>
        <div class="race-modal-content">
            <canvas id="confetti-canvas" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10000;"></canvas>
            <h2>${data.result_text}</h2>
            <p>${data.points_text}</p>
            <button id="claim-race-btn">Claim</button>
        </div>
    `;
    document.body.appendChild(modal);
    document.body.classList.add('race-modal-blur');
    // Animation
    if (data.result_text.includes('won')) {
        launchConfetti();
    } else if (data.result_text.includes('lose')) {
        document.querySelector('.race-modal-content').classList.add('shake-anim');
    }
    document.getElementById('claim-race-btn').onclick = function() {
        document.body.classList.remove('race-modal-blur');
        modal.remove();
        fetch('/race/claim_result', {method: 'POST'});
    };
}

// Confetti animation for winner
function launchConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    const confetti = [];
    for (let i = 0; i < 150; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: Math.random() * -canvas.height,
            r: Math.random() * 6 + 4,
            d: Math.random() * 100 + 10,
            color: `hsl(${Math.random()*360},100%,50%)`,
            tilt: Math.random() * 10 - 10
        });
    }
    let angle = 0;
    function drawConfetti() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < confetti.length; i++) {
            let c = confetti[i];
            ctx.beginPath();
            ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
            ctx.fillStyle = c.color;
            ctx.fill();
        }
        updateConfetti();
    }
    function updateConfetti() {
        angle += 0.01;
        for (let i = 0; i < confetti.length; i++) {
            let c = confetti[i];
            c.y += (Math.cos(angle + c.d) + 3 + c.r/2) / 2;
            c.x += Math.sin(angle);
            if (c.y > canvas.height) {
                c.x = Math.random() * canvas.width;
                c.y = Math.random() * -20;
            }
        }
    }
    let confettiInterval = setInterval(drawConfetti, 16);
    setTimeout(() => {
        clearInterval(confettiInterval);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }, 3000);
}

// Shake animation for loser
const style = document.createElement('style');
style.innerHTML = `
.shake-anim {
    animation: shake 0.7s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes shake {
    10%, 90% { transform: translate3d(-1px, 0, 0); }
    20%, 80% { transform: translate3d(2px, 0, 0); }
    30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
    40%, 60% { transform: translate3d(4px, 0, 0); }
}`;
document.head.appendChild(style);
}

setInterval(pollRaceResult, 5000); // poll every 5 seconds
