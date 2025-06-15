class TimerManager {
    constructor() {
        this.timers = new Map();
        this.intervals = new Map();
        this.fullscreenTaskId = null;
        this.loadTimerStates();
        this.startUpdateLoop();
        this.initializeFullscreenModal();
    }

    // Load timer states from localStorage
    loadTimerStates() {
        try {
            const saved = localStorage.getItem('timerStates');
            if (saved) {
                const states = JSON.parse(saved);
                const now = new Date();
                for (const [taskId, state] of Object.entries(states)) {
                    let newState = {
                        ...state,
                        startTime: state.startTime ? new Date(state.startTime) : null
                    };
                    // If timer was running, update elapsed and remaining based on time passed
                    if (newState.isRunning && newState.startTime) {
                        const elapsedMs = now - newState.startTime;
                        const elapsedSeconds = Math.floor(elapsedMs / 1000);
                        newState.elapsedSeconds = (newState.elapsedSeconds || 0) + elapsedSeconds;
                        newState.remainingSeconds = Math.max(0, newState.durationMinutes * 60 - newState.elapsedSeconds);
                        // If time is up, mark as not running
                        if (newState.remainingSeconds === 0) {
                            newState.isRunning = false;
                            newState.isPaused = false;
                        } else {
                            // Reset startTime to now for continued timing
                            newState.startTime = now;
                        }
                    }
                    this.timers.set(parseInt(taskId), newState);
                }
            }
        } catch (error) {
            console.error('Error loading timer states:', error);
            localStorage.removeItem('timerStates');
        }
    }

    // Save timer states to localStorage
    saveTimerStates() {
        try {
            const states = {};
            for (const [taskId, state] of this.timers.entries()) {
                states[taskId] = {
                    ...state,
                    startTime: state.startTime ? state.startTime.toISOString() : null
                };
            }
            localStorage.setItem('timerStates', JSON.stringify(states));
        } catch (error) {
            console.error('Error saving timer states:', error);
        }
    }

    // Start or resume a timer for a task
    startTimer(taskId, durationMinutes) {
        // Pause any other running timer
        for (const [otherTaskId, otherState] of this.timers.entries()) {
            if (otherTaskId !== taskId && otherState.isRunning) {
                this.pauseTimer(otherTaskId);
                break;
            }
        }

        const now = new Date();
        let state = this.timers.get(taskId);

        if (!state) {
            // New timer
            state = {
                durationMinutes: durationMinutes || 1, // fallback to 1 minute if undefined
                remainingSeconds: (durationMinutes || 1) * 60,
                elapsedSeconds: 0,
                isRunning: true,
                isPaused: false,
                startTime: now
            };
        } else {
            // Resume existing timer
            state.isRunning = true;
            state.isPaused = false;
            state.startTime = now;
            // Ensure durationMinutes and remainingSeconds are valid
            if (!state.durationMinutes) state.durationMinutes = durationMinutes || 1;
            if (typeof state.remainingSeconds !== 'number' || isNaN(state.remainingSeconds)) {
                state.remainingSeconds = state.durationMinutes * 60;
            }
        }

        this.timers.set(taskId, state);
        this.updateTimerControls(taskId, 'running');
        this.updateTimerDisplay(taskId);
        // Update fullscreen timer display if in fullscreen
        if (this.fullscreenTaskId === taskId) {
            const fullscreenTimer = document.getElementById('fullscreenTimer');
            if (fullscreenTimer) {
                fullscreenTimer.textContent = this.formatTime(state.remainingSeconds);
            }
        }
        this.saveTimerStates();
    }

    // Pause a running timer
    pauseTimer(taskId) {
        const state = this.timers.get(taskId);
        if (!state || !state.isRunning) return;

        state.isRunning = false;
        state.isPaused = true;
        const now = new Date();
        if (state.startTime) {
            const elapsedMs = now - state.startTime;
            const elapsedSeconds = Math.floor(elapsedMs / 1000);
            state.elapsedSeconds += elapsedSeconds;
            state.remainingSeconds = Math.max(0, state.durationMinutes * 60 - state.elapsedSeconds);
        }

        this.timers.set(taskId, state);
        this.updateTimerControls(taskId, 'paused');
        this.saveTimerStates();
    }

    // Resume a paused timer
    resumeTimer(taskId) {
        // Pause any other running timer
        for (const [otherTaskId, otherState] of this.timers.entries()) {
            if (otherTaskId !== taskId && otherState.isRunning) {
                this.pauseTimer(otherTaskId);
                break;
            }
        }

        const state = this.timers.get(taskId);
        if (!state || !state.isPaused) return;

        state.isRunning = true;
        state.isPaused = false;
        state.startTime = new Date();

        this.timers.set(taskId, state);
        this.updateTimerControls(taskId, 'running');
        this.saveTimerStates();
    }

    // Update timer display for a specific task
    updateTimerDisplay(taskId, remainingSeconds = null) {
        const timerElement = document.getElementById(`timer-${taskId}`);
        const state = this.timers.get(taskId);
        let seconds = remainingSeconds;

        if (seconds === null && state) {
            if (state.isRunning && state.startTime) {
                const now = new Date();
                const elapsedMs = now - state.startTime;
                const currentElapsed = Math.floor(elapsedMs / 1000);
                const totalElapsed = state.elapsedSeconds + currentElapsed;
                seconds = Math.max(0, state.durationMinutes * 60 - totalElapsed);
            } else {
                seconds = state.remainingSeconds;
            }
        }

        // Update main timer display
        if (timerElement) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            const timeStr = `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            const displayElement = timerElement.querySelector('.display-6');
            if (displayElement) {
                displayElement.textContent = timeStr;
                timerElement.classList.remove('running', 'paused', 'completed');
                if (state) {
                    if (seconds === 0) {
                        timerElement.classList.add('completed');
                    } else if (state.isRunning) {
                        timerElement.classList.add('running');
                    } else if (state.isPaused) {
                        timerElement.classList.add('paused');
                    }
                }
            }
        }

        // Always update fullscreen timer display if open
        if (this.fullscreenTaskId === taskId) {
            const fullscreenTimer = document.getElementById('fullscreenTimer');
            if (fullscreenTimer) {
                // Use the same logic as formatTime for HH:MM:SS
                let totalSeconds = seconds;
                if (isNaN(totalSeconds) || totalSeconds < 0) totalSeconds = 0;
                const hours = Math.floor(totalSeconds / 3600);
                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const secs = totalSeconds % 60;
                fullscreenTimer.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
            }
        }

        // Check if timer completed
        if (seconds === 0 && state && state.isRunning) {
            this.completeTask(taskId);
        }
    }

    // Update timer control buttons based on state
    updateTimerControls(taskId, timerState) {
        const startBtn = document.querySelector(`button[onclick*="startTimer(${taskId}"]`);
        const pauseBtn = document.getElementById(`pause-${taskId}`);
        const resumeBtn = document.getElementById(`resume-${taskId}`);

        if (!startBtn || !pauseBtn || !resumeBtn) return;

        startBtn.style.display = 'none';
        pauseBtn.style.display = 'none';
        resumeBtn.style.display = 'none';

        switch (timerState) {
            case 'idle':
                startBtn.style.display = 'inline-block';
                break;
            case 'running':
                pauseBtn.style.display = 'inline-block';
                break;
            case 'paused':
                resumeBtn.style.display = 'inline-block';
                break;
        }

        // Update fullscreen controls if modal is open
        if (this.fullscreenTaskId === taskId) {
            const fullscreenPause = document.getElementById('fullscreenPause');
            const fullscreenResume = document.getElementById('fullscreenResume');
            if (fullscreenPause && fullscreenResume) {
                fullscreenPause.style.display = timerState === 'running' ? 'inline-block' : 'none';
                fullscreenResume.style.display = timerState === 'paused' ? 'inline-block' : 'none';
            }
        }
    }

    // Complete a task automatically when timer reaches 00:00
    completeTask(taskId) {
        const state = this.timers.get(taskId);
        if (!state) return;

        state.isRunning = false;
        state.isPaused = false;
        state.remainingSeconds = 0;
        state.elapsedSeconds = state.durationMinutes * 60;

        this.timers.set(taskId, state);
        this.updateTimerControls(taskId, 'completed');
        this.saveTimerStates();

        const actualMinutes = Math.ceil(state.elapsedSeconds / 60);
        this.submitTaskCompletion(taskId, actualMinutes);

        const taskCard = document.querySelector(`#timer-${taskId}`).closest('.task-card');
        if (taskCard) {
            taskCard.classList.add('task-completed');
        }

        if (this.fullscreenTaskId === taskId) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('fullscreenTimerModal'));
            if (modal) {
                modal.hide();
            }
        }
    }

    // Submit task completion form
    submitTaskCompletion(taskId, actualMinutes) {
        const form = document.getElementById('completeTaskForm');
        if (!form) return;

        const taskIdInput = form.querySelector('input[name="task_id"]');
        const actualMinutesInput = form.querySelector('input[name="actual_minutes"]');

        if (taskIdInput && actualMinutesInput) {
            taskIdInput.value = taskId;
            actualMinutesInput.value = actualMinutes;
            HTMLFormElement.prototype.submit.call(form);
        }
    }

    // Open fullscreen timer modal
    openFullscreen(taskId, taskName, durationMinutes) {
        this.fullscreenTaskId = taskId;
        this.fullscreenTaskDuration = durationMinutes; // Store the correct duration
        document.getElementById('fullscreenTaskName').textContent = taskName;
        // Ensure timer display is valid
        const state = this.timers.get(taskId);
        let displayTime = '00:00:00';
        if (state && typeof state.remainingSeconds === 'number') {
            displayTime = this.formatTime(state.remainingSeconds);
        } else if (state && typeof state.durationMinutes === 'number') {
            displayTime = this.formatTime(state.durationMinutes * 60);
        } else if (typeof durationMinutes === 'number') {
            displayTime = this.formatTime(durationMinutes * 60);
        }
        const fullscreenTimer = document.getElementById('fullscreenTimer');
        if (fullscreenTimer) fullscreenTimer.textContent = displayTime;
        if (state) {
            if (state.isRunning) {
                this.updateTimerControls(taskId, 'running');
            } else if (state.isPaused) {
                this.updateTimerControls(taskId, 'paused');
            } else {
                this.updateTimerControls(taskId, 'idle');
            }
        }
        const modal = new bootstrap.Modal(document.getElementById('fullscreenTimerModal'));
        modal.show();
    }

    // Helper to format seconds as HH:MM:SS
    formatTime(totalSeconds) {
        if (isNaN(totalSeconds) || totalSeconds < 0) totalSeconds = 0;
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        return (
            String(hours).padStart(2, '0') + ':' +
            String(minutes).padStart(2, '0') + ':' +
            String(seconds).padStart(2, '0')
        );
    }

    // Initialize fullscreen modal event handlers
    initializeFullscreenModal() {
        const modal = document.getElementById('fullscreenTimerModal');
        const pauseBtn = document.getElementById('fullscreenPause');
        const resumeBtn = document.getElementById('fullscreenResume');

        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (this.fullscreenTaskId !== null) {
                    this.pauseTimer(this.fullscreenTaskId);
                }
            });
        }

        if (resumeBtn) {
            resumeBtn.addEventListener('click', () => {
                if (this.fullscreenTaskId !== null) {
                    this.resumeTimer(this.fullscreenTaskId);
                }
            });
        }

        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.fullscreenTaskId = null;
            });
        }
    }

    // Update all active timers
    updateAllTimers() {
        for (const [taskId, state] of this.timers.entries()) {
            if (state.isRunning) {
                const now = new Date();
                if (state.startTime) {
                    const elapsedMs = now - state.startTime;
                    const currentElapsed = Math.floor(elapsedMs / 1000);
                    const totalElapsed = state.elapsedSeconds + currentElapsed;
                    const remaining = Math.max(0, state.durationMinutes * 60 - totalElapsed);
                    this.updateTimerDisplay(taskId, remaining);
                    if (remaining === 0) {
                        this.completeTask(taskId);
                    }
                }
            }
        }
    }

    // Start the main update loop
    startUpdateLoop() {
        setInterval(() => {
            this.updateAllTimers();
        }, 1000);
    }

    // Clean up completed or deleted tasks from storage
    cleanupStorage() {
        const taskElements = document.querySelectorAll('[id^="timer-"]');
        const existingTaskIds = new Set();
        taskElements.forEach(element => {
            const taskId = parseInt(element.id.replace('timer-', ''));
            existingTaskIds.add(taskId);
        });
        for (const taskId of this.timers.keys()) {
            if (!existingTaskIds.has(taskId)) {
                this.timers.delete(taskId);
                if (this.intervals.has(taskId)) {
                    clearInterval(this.intervals.get(taskId));
                    this.intervals.delete(taskId);
                }
            }
        }
        this.saveTimerStates();
    }
}

// Theme toggle logic (global)
function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const icon = document.querySelector('#theme-toggle i');
    const text = document.getElementById('theme-toggle-text');
    if (icon && text) {
        if (theme === 'dark') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            text.textContent = 'Light Mode';
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            text.textContent = 'Dark Mode';
        }
    }
    // Swap fullscreen background image
    const fullscreenBg = document.getElementById('fullscreenBgImage');
    if (fullscreenBg) {
        if (theme === 'dark') {
            fullscreenBg.src = '/static/images/forest2.jpg';
        } else {
            fullscreenBg.src = '/static/images/forest.jpg';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.timerManager = new TimerManager();
    window.timerManager.cleanupStorage();
    for (const [taskId, state] of window.timerManager.timers.entries()) {
        if (state.isRunning) {
            window.timerManager.updateTimerControls(taskId, 'running');
        } else if (state.isPaused) {
            window.timerManager.updateTimerControls(taskId, 'paused');
        } else {
            window.timerManager.updateTimerControls(taskId, 'idle');
        }
        window.timerManager.updateTimerDisplay(taskId);
    }
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && window.timerManager.fullscreenTaskId !== null) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('fullscreenTimerModal'));
            if (modal) {
                modal.hide();
            }
        }
        if (event.key === ' ' && window.timerManager.fullscreenTaskId !== null) {
            event.preventDefault();
            const taskId = window.timerManager.fullscreenTaskId;
            const state = window.timerManager.timers.get(taskId);
            if (state && state.isRunning) {
                window.timerManager.pauseTimer(taskId);
            } else if (state && state.isPaused) {
                window.timerManager.resumeTimer(taskId);
            }
        }
    });

    // Set theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const current = document.body.getAttribute('data-theme') || 'light';
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (window.timerManager) {
        window.timerManager.saveTimerStates();
    }
});