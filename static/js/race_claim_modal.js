// Race Claim Modal Logic

document.addEventListener('DOMContentLoaded', function() {
    if (!window.currentUserId) return;
    fetch('/get_unclaimed_race')
        .then(res => res.json())
        .then(data => {
            if (data && data.show) {
                showRaceClaimModal(data);
            }
        });

    function showRaceClaimModal(data) {
        const modal = document.getElementById('race-claim-modal');
        const blur = document.getElementById('race-claim-blur');
        const img = document.getElementById('race-claim-user-img');
        const username = document.getElementById('race-claim-username');
        const message = document.getElementById('race-claim-message');
        const btn = document.getElementById('race-claim-btn');

        img.src = data.user_img;
        username.textContent = data.username;
        message.textContent = data.message;
        modal.style.display = 'flex';
        blur.style.display = 'block';
        document.body.style.overflow = 'hidden';

        btn.onclick = function() {
            btn.disabled = true;
            fetch('/claim_race_points', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ race_id: data.race_id })
            })
            .then(res => res.json())
            .then(resp => {
                modal.style.display = 'none';
                blur.style.display = 'none';
                document.body.style.overflow = '';
                if (resp.success) {
                    // Optionally update points in UI
                    location.reload();
                } else {
                    alert(resp.message || 'Error claiming points.');
                }
            });
        };
    }
});
