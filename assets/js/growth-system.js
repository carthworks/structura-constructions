/**
 * MIN MURASU — CONSTRUCTION GROWTH SYSTEM
 * Interactive 3-Minute Demo Controller, WhatsApp Simulator & Commercial ROI Engine
 */

(function () {
  "use strict";

  function $(sel, parent) { return (parent || document).querySelector(sel); }
  function $$(sel, parent) { return Array.prototype.slice.call((parent || document).querySelectorAll(sel)); }

  /* -------------------------------------------------------------
     1. Interactive 5-Step Simulator Tabs
     ------------------------------------------------------------- */
  var tabButtons = $$(".demo-tab-btn");
  var stagePanels = $$(".demo-stage-panel");
  var currentStep = 1;
  var totalSteps = 6;

  function setStep(step) {
    currentStep = step;
    tabButtons.forEach(function (btn) {
      var isAct = parseInt(btn.getAttribute("data-step"), 10) === step;
      btn.classList.toggle("is-active", isAct);
      btn.setAttribute("aria-selected", isAct ? "true" : "false");
    });

    stagePanels.forEach(function (panel) {
      var isAct = parseInt(panel.getAttribute("data-step"), 10) === step;
      panel.classList.toggle("is-active", isAct);
      panel.style.display = isAct ? "grid" : "none";
    });

    // Also highlight the corresponding flowchart node if on page
    $$(".system-node").forEach(function (node) {
      var isAct = parseInt(node.getAttribute("data-step"), 10) === step;
      node.classList.toggle("is-active", isAct);
    });
  }

  tabButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var step = parseInt(btn.getAttribute("data-step"), 10);
      setStep(step);
    });
  });

  $$(".system-node").forEach(function (node) {
    node.addEventListener("click", function () {
      var step = parseInt(node.getAttribute("data-step"), 10);
      setStep(step);
      var demoBox = $("#demoWalkthrough");
      if (demoBox) demoBox.scrollIntoView({ behavior: "smooth" });
    });
  });

  /* -------------------------------------------------------------
     2. 3-Minute Presentation Timer
     ------------------------------------------------------------- */
  var timerDisplay = $("#presoTimer");
  var timerBtn = $("#presoTimerBtn");
  var timerSeconds = 180; // 3 minutes
  var timerInterval = null;
  var isTimerRunning = false;

  function updateTimerDisplay() {
    if (!timerDisplay) return;
    var mins = Math.floor(timerSeconds / 60);
    var secs = timerSeconds % 60;
    timerDisplay.textContent = (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
  }

  function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    isTimerRunning = true;
    if (timerBtn) timerBtn.textContent = "⏸ Pause Walkthrough";

    timerInterval = setInterval(function () {
      if (timerSeconds > 0) {
        timerSeconds--;
        updateTimerDisplay();

        // Auto step progression every 30s (180s / 6 steps = 30s per step)
        var elapsed = 180 - timerSeconds;
        var nextCalculatedStep = Math.min(totalSteps, Math.floor(elapsed / 30) + 1);
        if (nextCalculatedStep !== currentStep) {
          setStep(nextCalculatedStep);
        }
      } else {
        clearInterval(timerInterval);
        isTimerRunning = false;
        if (timerBtn) timerBtn.textContent = "✓ Demo Completed";
      }
    }, 1000);
  }

  function pauseTimer() {
    clearInterval(timerInterval);
    isTimerRunning = false;
    if (timerBtn) timerBtn.textContent = "▶ Resume Walkthrough";
  }

  if (timerBtn) {
    timerBtn.addEventListener("click", function () {
      if (isTimerRunning) {
        pauseTimer();
      } else {
        if (timerSeconds <= 0) {
          timerSeconds = 180;
          setStep(1);
        }
        startTimer();
      }
    });
  }

  var timerResetBtn = $("#presoTimerReset");
  if (timerResetBtn) {
    timerResetBtn.addEventListener("click", function () {
      clearInterval(timerInterval);
      isTimerRunning = false;
      timerSeconds = 180;
      updateTimerDisplay();
      setStep(1);
      if (timerBtn) timerBtn.textContent = "▶ Start 3-Min Demo";
    });
  }

  /* -------------------------------------------------------------
     3. WhatsApp Simulator (Step 4)
     ------------------------------------------------------------- */
  var waChatArea = $("#waChatArea");
  var waInput = $("#waSimInput");
  var waSendBtn = $("#waSimSend");
  var waChips = $$(".wa-chip");

  function appendWaMessage(text, isIncoming) {
    if (!waChatArea) return;
    var d = new Date();
    var timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    var bubble = document.createElement("div");
    bubble.className = "wa-bubble " + (isIncoming ? "wa-bubble--incoming" : "wa-bubble--outgoing");
    bubble.innerHTML = text + '<span class="wa-time">' + timeStr + '</span>';
    waChatArea.appendChild(bubble);
    waChatArea.scrollTop = waChatArea.scrollHeight;
  }

  function triggerWaSimulation(userText) {
    if (!userText || !userText.trim()) return;
    appendWaMessage(userText, false);
    if (waInput) waInput.value = "";

    // Show simulated AI bot response after 1.2s
    setTimeout(function () {
      var refId = "STR-" + Math.floor(1000 + Math.random() * 9000);
      var replyHtml = '<strong>Structura Constructions AI Assistant</strong><br>' +
        'Thank you for reaching out! Your project brief has been recorded under Ref <code>#' + refId + '</code>.<br><br>' +
        '📋 <strong>Next immediate action:</strong> A civil engineer has been notified for site feasibility.<br>' +
        '📁 <a href="index.html#projects" style="color:#38BDF8;text-decoration:underline">Download Commercial Portfolio PDF</a>';
      appendWaMessage(replyHtml, true);

      // Trigger simulated site engineer SMS alert
      var engineerAlert = $("#engineerAlertBox");
      if (engineerAlert) {
        engineerAlert.classList.add("is-visible");
        var alertText = $("#engineerAlertText");
        if (alertText) {
          alertText.textContent = "SMS dispatched to Site Head: Ref #" + refId + " — " + userText.substring(0, 45) + "...";
        }
      }
    }, 1200);
  }

  if (waSendBtn && waInput) {
    waSendBtn.addEventListener("click", function () {
      triggerWaSimulation(waInput.value);
    });
    waInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") triggerWaSimulation(waInput.value);
    });
  }

  waChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var sampleText = chip.getAttribute("data-text");
      if (sampleText) triggerWaSimulation(sampleText);
    });
  });

  /* -------------------------------------------------------------
     4. Commercial Value & ROI Calculator
     ------------------------------------------------------------- */
  var avgDealRange = $("#roiAvgDeal");
  var dealMarginRange = $("#roiMargin");
  var wonDealsRange = $("#roiWonDeals");

  var avgDealVal = $("#roiAvgDealVal");
  var dealMarginVal = $("#roiMarginVal");
  var wonDealsVal = $("#roiWonDealsVal");

  var outRevenue = $("#roiOutRevenue");
  var outProfit = $("#roiOutProfit");
  var outMultiple = $("#roiOutMultiple");

  function formatIndianCurrency(num) {
    if (num >= 10000000) {
      return "₹" + (num / 10000000).toFixed(2) + " Crore";
    }
    if (num >= 100000) {
      return "₹" + (num / 100000).toFixed(1) + " Lakh";
    }
    return "₹" + num.toLocaleString("en-IN");
  }

  function calculateRoi() {
    if (!avgDealRange || !dealMarginRange || !wonDealsRange) return;

    var dealSizeLakhs = parseFloat(avgDealRange.value); // in Lakhs
    var marginPct = parseFloat(dealMarginRange.value); // in %
    var dealsCount = parseInt(wonDealsRange.value, 10);

    // Update displays
    if (avgDealVal) {
      if (dealSizeLakhs >= 100) {
        avgDealVal.textContent = "₹" + (dealSizeLakhs / 100).toFixed(1) + " Cr";
      } else {
        avgDealVal.textContent = "₹" + dealSizeLakhs + " Lakh";
      }
    }
    if (dealMarginVal) dealMarginVal.textContent = marginPct + "%";
    if (wonDealsVal) wonDealsVal.textContent = dealsCount + " project" + (dealsCount > 1 ? "s" : "");

    var dealSizeRupees = dealSizeLakhs * 100000;
    var totalAddedRevenue = dealSizeRupees * dealsCount;
    var totalAddedNetProfit = totalAddedRevenue * (marginPct / 100);

    // Benchmark Min Murasu Growth Partnership Annual Fee (approx ₹3.5 Lakh / yr)
    var annualInvestment = 350000;
    var roiMultiplier = Math.round(totalAddedNetProfit / annualInvestment);

    if (outRevenue) outRevenue.textContent = formatIndianCurrency(totalAddedRevenue);
    if (outProfit) outProfit.textContent = formatIndianCurrency(totalAddedNetProfit);
    if (outMultiple) outMultiple.textContent = (roiMultiplier > 0 ? roiMultiplier : 1) + "x ROI";
  }

  if (avgDealRange && dealMarginRange && wonDealsRange) {
    avgDealRange.addEventListener("input", calculateRoi);
    dealMarginRange.addEventListener("input", calculateRoi);
    wonDealsRange.addEventListener("input", calculateRoi);
    calculateRoi();
  }

  // Set default initial view
  setStep(1);
  updateTimerDisplay();

  /* -------------------------------------------------------------
     5. Keyboard support for flowchart nodes (Enter / Space)
     ------------------------------------------------------------- */
  $$(".system-node").forEach(function (node) {
    node.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); node.click(); }
    });
  });

  /* -------------------------------------------------------------
     6. Theme toggle (this page does not load main.js)
     ------------------------------------------------------------- */
  $$("#themeToggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var toLight = document.documentElement.getAttribute("data-theme") !== "light";
      if (toLight) document.documentElement.setAttribute("data-theme", "light");
      else document.documentElement.removeAttribute("data-theme");
      try { localStorage.setItem("structura-theme", toLight ? "light" : "dark"); } catch (e) {}
      var meta = $('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", toLight ? "#F8FAFC" : "#070C14");
    });
  });

})();

