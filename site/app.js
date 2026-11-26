/**
 * Japan Resort Zoning & Yield — Clean Minimalist Interactive App
 * Explorer, 180d-vs-365d Yield Calculator & Bilingual Gyoseishoshi Referral Desk
 */
(function () {
  "use strict";

  // Partner configuration: connect a bilingual Gyoseishoshi firm or STR operator in 1 line.
  // Zero upfront checkout = zero Specified Commercial Transactions Act burden (pure B2B/investor referral).
  const PARTNER_CONFIG = {
    deskDisplayName: "Japan Resort Hospitality & Gyoseishoshi Referral Desk",
    intakeEmail: "chaochenxuanhua@gmail.com",
    webhookEndpointUrl: "", // Optional Formspree / Make / Zapier HTTPS endpoint
    partnerBookingUrl: ""   // Optional direct partner intake URL
  };

  const state = {
    resorts: [],
    summary: null,
    fxRate: 152.0,
    viewMode: "grid",
    activeModalResortId: null,
    selectedCalcResortId: "hakuba",
    lastUnderwriting: null
  };

  function fmtJpy(amount) {
    const rounded = Math.round(Number(amount) || 0);
    const sign = rounded < 0 ? "-" : "";
    return sign + "\u00a5" + Math.abs(rounded).toLocaleString("en-US");
  }

  function fmtUsd(jpyAmount) {
    const rate = Math.max(1, Number(state.fxRate) || 152);
    const usd = Math.round((Number(jpyAmount) || 0) / rate);
    const sign = usd < 0 ? "-" : "";
    return sign + "$" + Math.abs(usd).toLocaleString("en-US");
  }

  function fmtDual(jpyAmount) {
    return fmtJpy(jpyAmount) + " (" + fmtUsd(jpyAmount) + ")";
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
  }

  function severityBadgeClass(severity) {
    if (String(severity).startsWith("Green")) return "badge-green";
    if (String(severity).startsWith("Amber")) return "badge-amber";
    return "badge-red";
  }

  function severityDotClass(severity) {
    if (String(severity).startsWith("Green")) return "dot-green";
    if (String(severity).startsWith("Amber")) return "dot-amber";
    return "dot-red";
  }

  function feasibilityBadgeClass(feasibility) {
    if (String(feasibility).startsWith("High")) return "badge-green";
    if (String(feasibility).startsWith("Moderate")) return "badge-amber";
    return "badge-red";
  }

  function feasibilityDotClass(feasibility) {
    if (String(feasibility).startsWith("High")) return "dot-green";
    if (String(feasibility).startsWith("Moderate")) return "dot-amber";
    return "dot-red";
  }

  async function loadOrdinanceDataset() {
    try {
      const resp = await fetch("./data/resort_ordinances.json", { cache: "no-store" });
      if (resp.ok) {
        return await resp.json();
      }
    } catch (_err) {
      // Fallback for direct file:// opening without local HTTP server
    }
    if (window.__RESORT_ORDINANCES_DATA__) {
      return window.__RESORT_ORDINANCES_DATA__;
    }
    throw new Error("Unable to load resort_ordinances.json dataset.");
  }

  function populateDropdowns() {
    const prefSelect = document.getElementById("prefectureSelect");
    const calcPreset = document.getElementById("calcResortPreset");
    const leadResort = document.getElementById("leadResort");

    const prefectures = Array.from(new Set(state.resorts.map((r) => r.prefecture))).sort();
    prefectures.forEach((pref) => {
      const opt = document.createElement("option");
      opt.value = pref;
      opt.textContent = pref;
      prefSelect.appendChild(opt);
    });

    calcPreset.innerHTML = "";
    leadResort.innerHTML = "";

    state.resorts.forEach((resort) => {
      const label =
        resort.name +
        " (" +
        resort.prefecture +
        " \u00b7 Minpaku ~" +
        resort.effective_minpaku_days_typical +
        "d vs 365d)";

      const optCalc = document.createElement("option");
      optCalc.value = resort.id;
      optCalc.textContent = label;
      calcPreset.appendChild(optCalc);

      const optLead = document.createElement("option");
      optLead.value = resort.id;
      optLead.textContent = resort.name + " - " + resort.japanese_name;
      leadResort.appendChild(optLead);
    });
  }

  function getFilteredResorts() {
    const q = document.getElementById("searchInput").value.trim().toLowerCase();
    const cat = document.getElementById("categorySelect").value;
    const sev = document.getElementById("severitySelect").value;
    const feas = document.getElementById("feasibilitySelect").value;
    const pref = document.getElementById("prefectureSelect").value;

    return state.resorts.filter((r) => {
      if (cat !== "ALL" && r.resort_category !== cat) return false;
      if (sev !== "ALL" && r.minpaku_severity !== sev) return false;
      if (feas !== "ALL" && r.ryokan_365_feasibility !== feas) return false;
      if (pref !== "ALL" && r.prefecture !== pref) return false;
      if (q) {
        const haystack = [
          r.name,
          r.japanese_name,
          r.prefecture,
          r.resort_category,
          r.minpaku_severity,
          r.minpaku_ordinance_summary,
          r.ryokan_365_feasibility,
          r.ryokan_365_zoning_notes,
          r.fire_safety_and_building_notes,
          r.local_lodging_tax_notes,
          r.ordinance_jurisdiction
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }

  function renderExplorer() {
    const filtered = getFilteredResorts();
    const countLabel = document.getElementById("filterCountLabel");
    countLabel.innerHTML =
      "Showing <strong>" +
      filtered.length +
      "</strong> of " +
      state.resorts.length +
      " resort markets";

    const gridEl = document.getElementById("explorerGrid");
    const tableWrap = document.getElementById("explorerTableWrap");
    const tableBody = document.getElementById("explorerTableBody");

    if (state.viewMode === "grid") {
      gridEl.classList.remove("hidden");
      tableWrap.classList.add("hidden");
    } else {
      gridEl.classList.add("hidden");
      tableWrap.classList.remove("hidden");
    }

    if (filtered.length === 0) {
      gridEl.innerHTML =
        '<div class="resort-card"><p class="card-summary">No resort markets match the active filters. Click "Reset filters" to view all 20 markets.</p></div>';
      tableBody.innerHTML =
        '<tr><td colspan="8">No resort markets match the active filters.</td></tr>';
      return;
    }

    gridEl.innerHTML = filtered
      .map((r) => {
        const sevClass = severityBadgeClass(r.minpaku_severity);
        const sevDot = severityDotClass(r.minpaku_severity);
        const feasClass = feasibilityBadgeClass(r.ryokan_365_feasibility);
        const feasDot = feasibilityDotClass(r.ryokan_365_feasibility);
        const bm = r.benchmark_metrics;
        return (
          '<article class="resort-card" data-resort-id="' +
          escapeHtml(r.id) +
          '">' +
          "<div>" +
          '<div class="card-top">' +
          "<div>" +
          '<h3 class="card-title">' +
          escapeHtml(r.name) +
          "</h3>" +
          '<div class="card-jp">' +
          escapeHtml(r.japanese_name) +
          " \u00b7 " +
          escapeHtml(r.prefecture) +
          "</div>" +
          "</div>" +
          '<span class="badge badge-cat">' +
          escapeHtml(r.resort_category) +
          "</span>" +
          "</div>" +
          '<div class="badge-row">' +
          '<span class="badge ' +
          sevClass +
          '"><span class="status-dot ' +
          sevDot +
          '" aria-hidden="true"></span>Minpaku: ' +
          escapeHtml(r.minpaku_severity) +
          "</span>" +
          '<span class="badge ' +
          feasClass +
          '"><span class="status-dot ' +
          feasDot +
          '" aria-hidden="true"></span>365d: ' +
          escapeHtml(r.ryokan_365_feasibility) +
          "</span>" +
          "</div>" +
          '<div class="card-Cap-strip">' +
          '<div class="cap-cell"><span>Effective Minpaku Cap</span><strong>~' +
          r.effective_minpaku_days_typical +
          " days/yr</strong></div>" +
          '<div class="cap-cell"><span>Peak ADR Benchmark</span><strong>' +
          fmtJpy(bm.peak_adr_jpy) +
          " (" +
          fmtUsd(bm.peak_adr_jpy) +
          ")</strong></div>" +
          "</div>" +
          '<p class="card-summary">' +
          escapeHtml(r.minpaku_ordinance_summary) +
          "</p>" +
          '<a href="./markets/' +
          escapeHtml(r.id) +
          '.html" class="card-guide-link">Full ' +
          escapeHtml(r.name) +
          " Zoning &amp; Yield Guide &rarr;</a>" +
          "</div>" +
          '<div class="card-actions">' +
          '<button type="button" class="btn-secondary js-open-modal" data-id="' +
          escapeHtml(r.id) +
          '">Ordinance Details</button>' +
          '<button type="button" class="btn-primary js-load-calc" data-id="' +
          escapeHtml(r.id) +
          '">Simulate Yield</button>' +
          "</div>" +
          "</article>"
        );
      })
      .join("");

    tableBody.innerHTML = filtered
      .map((r) => {
        const sevClass = severityBadgeClass(r.minpaku_severity);
        const sevDot = severityDotClass(r.minpaku_severity);
        const feasClass = feasibilityBadgeClass(r.ryokan_365_feasibility);
        const feasDot = feasibilityDotClass(r.ryokan_365_feasibility);
        return (
          "<tr>" +
          "<td><strong>" +
          escapeHtml(r.name) +
          "</strong><br/><small>" +
          escapeHtml(r.japanese_name) +
          "</small></td>" +
          "<td>" +
          escapeHtml(r.prefecture) +
          "</td>" +
          "<td>" +
          escapeHtml(r.resort_category) +
          "</td>" +
          '<td><span class="badge ' +
          sevClass +
          '"><span class="status-dot ' +
          sevDot +
          '" aria-hidden="true"></span>' +
          escapeHtml(r.minpaku_severity) +
          "</span></td>" +
          "<td><strong>~" +
          r.effective_minpaku_days_typical +
          "d</strong> / 180d</td>" +
          '<td><span class="badge ' +
          feasClass +
          '"><span class="status-dot ' +
          feasDot +
          '" aria-hidden="true"></span>' +
          escapeHtml(r.ryokan_365_feasibility) +
          "</span></td>" +
          "<td>" +
          fmtDual(r.benchmark_metrics.peak_adr_jpy) +
          "</td>" +
          '<td class="table-action-cell">' +
          '<button type="button" class="btn-secondary js-open-modal" data-id="' +
          escapeHtml(r.id) +
          '">Details</button>' +
          '<button type="button" class="btn-primary js-load-calc" data-id="' +
          escapeHtml(r.id) +
          '">Simulate</button>' +
          "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  function openModal(resortId) {
    const resort = state.resorts.find((r) => r.id === resortId);
    if (!resort) return;
    state.activeModalResortId = resort.id;

    document.getElementById("modalCategoryBadge").className = "badge badge-cat";
    document.getElementById("modalCategoryBadge").textContent =
      resort.resort_category + " \u00b7 " + resort.prefecture;
    document.getElementById("modalTitle").textContent =
      resort.name + " (" + resort.japanese_name + ")";
    document.getElementById("modalSubtitle").textContent =
      resort.ordinance_jurisdiction +
      " \u00b7 Verified " +
      resort.verified_at.slice(0, 10);

    const sevClass = severityBadgeClass(resort.minpaku_severity);
    const sevDot = severityDotClass(resort.minpaku_severity);
    const feasClass = feasibilityBadgeClass(resort.ryokan_365_feasibility);
    const feasDot = feasibilityDotClass(resort.ryokan_365_feasibility);

    document.getElementById("modalBody").innerHTML =
      '<div class="modal-section">' +
      '<h4>180-Day Minpaku &amp; Local Article 18 Ordinance <span class="badge ' +
      sevClass +
      '"><span class="status-dot ' +
      sevDot +
      '" aria-hidden="true"></span>' +
      escapeHtml(resort.minpaku_severity) +
      " (~" +
      resort.effective_minpaku_days_typical +
      "d/yr)</span></h4>" +
      "<p>" +
      escapeHtml(resort.minpaku_ordinance_summary) +
      "</p>" +
      "</div>" +
      '<div class="modal-section">' +
      '<h4>365-Day Ryokan-gyo (Simple Lodging / 簡易宿所) Zoning <span class="badge ' +
      feasClass +
      '"><span class="status-dot ' +
      feasDot +
      '" aria-hidden="true"></span>' +
      escapeHtml(resort.ryokan_365_feasibility) +
      "</span></h4>" +
      "<p>" +
      escapeHtml(resort.ryokan_365_zoning_notes) +
      "</p>" +
      "</div>" +
      '<div class="modal-section">' +
      "<h4>Fire Safety (Jikah\u014d), Front-Desk &amp; Building Standards</h4>" +
      "<p>" +
      escapeHtml(resort.fire_safety_and_building_notes) +
      "</p>" +
      "</div>" +
      '<div class="modal-section">' +
      "<h4>Accommodation Tax &amp; Onsen Bath Tax</h4>" +
      "<p>" +
      escapeHtml(resort.local_lodging_tax_notes) +
      "</p>" +
      "</div>" +
      '<div class="modal-section modal-citations">' +
      "<h4>Official Government Ordinance Sources</h4>" +
      '<p><strong>Prefectural / Municipal Portal:</strong> <a href="' +
      escapeHtml(resort.official_url) +
      '" target="_blank" rel="noopener noreferrer">' +
      escapeHtml(resort.official_url) +
      "</a></p>" +
      '<p class="modal-citation-follow"><strong>MLIT Minpaku Registry:</strong> <a href="' +
      escapeHtml(resort.secondary_mlit_url) +
      '" target="_blank" rel="noopener noreferrer">' +
      escapeHtml(resort.secondary_mlit_url) +
      "</a></p>" +
      '<p class="modal-citation-follow"><strong>Dedicated Market Guide:</strong> <a href="./markets/' +
      escapeHtml(resort.id) +
      '.html">Open ' +
      escapeHtml(resort.name) +
      " Standalone Zoning &amp; Yield Page</a></p>" +
      "</div>" +
      '<div class="modal-section modal-disclaimer">' +
      "<strong>Legal Notice:</strong> Zoning boundaries (<em>Y\u014dto Chiiki</em>), private villa covenants, septic rules, and road-frontage requirements vary lot by lot. Confirm parcel eligibility with a licensed Administrative Scrivener (<em>Gy\u014dseishoshi</em>) prior to signing a Purchase &amp; Sale Agreement." +
      "</div>";

    document.getElementById("ordinanceModal").classList.remove("hidden");
  }

  function closeModal() {
    document.getElementById("ordinanceModal").classList.add("hidden");
    state.activeModalResortId = null;
  }

  function applyResortPresetToCalculator(resortId, shouldScroll) {
    const resort = state.resorts.find((r) => r.id === resortId);
    if (!resort) return;
    state.selectedCalcResortId = resort.id;

    document.getElementById("calcResortPreset").value = resort.id;
    document.getElementById("leadResort").value = resort.id;

    const bm = resort.benchmark_metrics;
    document.getElementById("inpPriceJpy").value = bm.typical_price_jpy;
    document.getElementById("inpRenoJpy").value = bm.typical_renovation_capex_jpy;
    document.getElementById("inpFireUpgradeJpy").value = bm.fire_license_upgrade_capex_jpy;
    document.getElementById("inpPeakAdrJpy").value = bm.peak_adr_jpy;
    document.getElementById("inpOffpeakAdrJpy").value = bm.offpeak_adr_jpy;
    document.getElementById("inpPeakMonths").value = bm.peak_months;
    document.getElementById("inpPeakOccPct").value = bm.peak_occupancy_pct;
    document.getElementById("inpOffpeakOccPct").value = bm.offpeak_occupancy_pct;
    document.getElementById("inpFixedOpexJpy").value = bm.annual_fixed_opex_jpy;
    document.getElementById("inpMinpakuCapDays").value = resort.effective_minpaku_days_typical;

    document.getElementById("calcOrdinanceCallout").textContent =
      resort.name +
      ": " +
      resort.minpaku_severity +
      " (~" +
      resort.effective_minpaku_days_typical +
      " effective Minpaku days/yr vs 365-day Ryokan-gyo).";

    calculateYieldComparison();

    if (shouldScroll) {
      document.getElementById("simulator").scrollIntoView({ behavior: "smooth" });
    }
  }

  function calculateYieldComparison() {
    const resort =
      state.resorts.find((r) => r.id === state.selectedCalcResortId) || state.resorts[0];

    const priceJpy = Math.max(0, Number(document.getElementById("inpPriceJpy").value) || 0);
    const closingPct = Math.max(0, Number(document.getElementById("inpClosingPct").value) || 0);
    const renoJpy = Math.max(0, Number(document.getElementById("inpRenoJpy").value) || 0);
    const fireUpgradeJpy = Math.max(
      0,
      Number(document.getElementById("inpFireUpgradeJpy").value) || 0
    );
    const peakAdrJpy = Math.max(0, Number(document.getElementById("inpPeakAdrJpy").value) || 0);
    const offpeakAdrJpy = Math.max(
      0,
      Number(document.getElementById("inpOffpeakAdrJpy").value) || 0
    );
    const peakMonths = Math.min(
      11,
      Math.max(1, Number(document.getElementById("inpPeakMonths").value) || 4)
    );
    const minpakuCapDays = Math.min(
      180,
      Math.max(1, Number(document.getElementById("inpMinpakuCapDays").value) || 180)
    );
    const peakOccPct = Math.min(
      99,
      Math.max(1, Number(document.getElementById("inpPeakOccPct").value) || 75)
    );
    const offpeakOccPct = Math.min(
      99,
      Math.max(1, Number(document.getElementById("inpOffpeakOccPct").value) || 45)
    );
    const mgmtFeePct = Math.min(
      60,
      Math.max(0, Number(document.getElementById("inpMgmtFeePct").value) || 20)
    );
    const fixedOpexJpy = Math.max(
      0,
      Number(document.getElementById("inpFixedOpexJpy").value) || 0
    );

    document.getElementById("subPriceUsd").textContent = "Approx. " + fmtUsd(priceJpy);
    document.getElementById("subRenoUsd").textContent = "Approx. " + fmtUsd(renoJpy);
    document.getElementById("subFireUsd").textContent = "Approx. " + fmtUsd(fireUpgradeJpy);
    document.getElementById("subPeakAdrUsd").textContent = fmtUsd(peakAdrJpy) + " / night";
    document.getElementById("subOffpeakAdrUsd").textContent = fmtUsd(offpeakAdrJpy) + " / night";

    const peakCalendarDays = Math.round((peakMonths / 12) * 365);
    const offpeakCalendarDays = 365 - peakCalendarDays;

    const ryokanPeakNights = Math.round(peakCalendarDays * (peakOccPct / 100));
    const ryokanOffpeakNights = Math.round(offpeakCalendarDays * (offpeakOccPct / 100));
    const ryokanTotalNights = ryokanPeakNights + ryokanOffpeakNights;

    const severePeakWindowBan = minpakuCapDays <= 95;
    const maxAllowedPeakUnderMinpaku = severePeakWindowBan
      ? Math.round(minpakuCapDays * 0.45)
      : minpakuCapDays;

    const minpakuPeakNights = Math.min(ryokanPeakNights, maxAllowedPeakUnderMinpaku);
    const remainingMinpakuAllowance = Math.max(0, minpakuCapDays - minpakuPeakNights);
    const minpakuOffpeakNights = Math.min(ryokanOffpeakNights, remainingMinpakuAllowance);
    const minpakuTotalNights = minpakuPeakNights + minpakuOffpeakNights;

    const minpakuGrossRev =
      minpakuPeakNights * peakAdrJpy + minpakuOffpeakNights * offpeakAdrJpy;
    const ryokanGrossRev =
      ryokanPeakNights * peakAdrJpy + ryokanOffpeakNights * offpeakAdrJpy;

    const minpakuMgmtCost = Math.round(minpakuGrossRev * (mgmtFeePct / 100));
    const ryokanMgmtCost = Math.round(ryokanGrossRev * (mgmtFeePct / 100));

    const minpakuNoi = minpakuGrossRev - minpakuMgmtCost - fixedOpexJpy;
    const ryokanNoi = ryokanGrossRev - ryokanMgmtCost - fixedOpexJpy;

    const closingCostJpy = Math.round(priceJpy * (closingPct / 100));
    const basisMinpaku = priceJpy + closingCostJpy + renoJpy;
    const basisRyokan = basisMinpaku + fireUpgradeJpy;

    const yieldMinpaku = basisMinpaku > 0 ? (minpakuNoi / basisMinpaku) * 100 : 0;
    const yieldRyokan = basisRyokan > 0 ? (ryokanNoi / basisRyokan) * 100 : 0;

    const noiDelta = ryokanNoi - minpakuNoi;
    const extraNights = ryokanTotalNights - minpakuTotalNights;
    const paybackMonths =
      noiDelta > 0 ? (fireUpgradeJpy / (noiDelta / 12)).toFixed(1) : null;

    state.lastUnderwriting = {
      resort,
      priceJpy,
      renoJpy,
      fireUpgradeJpy,
      minpakuCapDays,
      minpakuTotalNights,
      ryokanTotalNights,
      minpakuGrossRev,
      ryokanGrossRev,
      minpakuNoi,
      ryokanNoi,
      basisMinpaku,
      basisRyokan,
      yieldMinpaku,
      yieldRyokan,
      noiDelta,
      paybackMonths
    };

    const signPrefix = noiDelta >= 0 ? "+" : "";
    document.getElementById("resNoiDeltaJpy").textContent = signPrefix + fmtJpy(noiDelta);
    document.getElementById("resNoiDeltaUsd").textContent =
      signPrefix + fmtUsd(noiDelta) + " / yr";
    document.getElementById("resYieldLift").textContent =
      yieldMinpaku.toFixed(2) + "% \u2192 " + yieldRyokan.toFixed(2) + "%";
    document.getElementById("resExtraNights").textContent =
      "+" + extraNights + " bookable nights/yr";
    document.getElementById("resPaybackPeriod").textContent = paybackMonths
      ? paybackMonths + " mos"
      : "N/A";

    const verdictEl = document.getElementById("verdictBox");
    if (resort && resort.ryokan_365_feasibility.startsWith("Strict")) {
      verdictEl.className = "verdict-box verdict-caution";
      verdictEl.innerHTML =
        "<strong>Zoning Note (" +
        escapeHtml(resort.name) +
        "):</strong> Upgrading to 365-day Simple Lodging adds <strong>" +
        fmtDual(noiDelta) +
        "/yr</strong>, but " +
        escapeHtml(resort.name) +
        " restricts residential hotel permits. Target Commercial or Permissive zoning with compliant check-in structure.";
    } else if (paybackMonths && Number(paybackMonths) <= 36) {
      verdictEl.className = "verdict-box verdict-positive";
      verdictEl.innerHTML =
        "<strong>Strong 365-Day License Upside:</strong> Investing " +
        fmtDual(fireUpgradeJpy) +
        " in commercial fire alarms (<em>Jikah\u014d</em>) and <em>Hokenjo</em> licensing pays back in <strong>" +
        paybackMonths +
        " months</strong> and lifts net yield by <strong>+" +
        (yieldRyokan - yieldMinpaku).toFixed(2) +
        "%</strong>.";
    } else {
      verdictEl.className = "verdict-box verdict-caution";
      verdictEl.innerHTML =
        "<strong>Moderate CapEx Payback:</strong> Under current ADR and occupancy settings, the 365-day upgrade pays back in " +
        (paybackMonths ? paybackMonths + " months." : "an extended timeframe.");
    }

    const maxScale = Math.max(ryokanGrossRev, minpakuGrossRev, 1);
    document.getElementById("barLabelMinpaku").textContent =
      fmtJpy(minpakuNoi) + " NOI (" + yieldMinpaku.toFixed(2) + "%)";
    document.getElementById("barLabelRyokan").textContent =
      fmtJpy(ryokanNoi) + " NOI (" + yieldRyokan.toFixed(2) + "%)";

    document.getElementById("barFillMinpakuRev").style.width =
      Math.max(0, (minpakuGrossRev / maxScale) * 100).toFixed(1) + "%";
    document.getElementById("barFillMinpakuNoi").style.width =
      Math.max(0, (Math.max(0, minpakuNoi) / maxScale) * 100).toFixed(1) + "%";
    document.getElementById("barFillRyokanRev").style.width =
      Math.max(0, (ryokanGrossRev / maxScale) * 100).toFixed(1) + "%";
    document.getElementById("barFillRyokanNoi").style.width =
      Math.max(0, (Math.max(0, ryokanNoi) / maxScale) * 100).toFixed(1) + "%";

    const rows = [
      [
        "Legal Operating Ceiling",
        minpakuCapDays + " days/yr (Ordinance Cap)",
        "365 days/yr (Commercial Permit)",
        ""
      ],
      [
        "Realized Booked Nights (Peak / Off-Peak)",
        minpakuTotalNights +
          " nights (" +
          minpakuPeakNights +
          "p / " +
          minpakuOffpeakNights +
          "o)",
        ryokanTotalNights +
          " nights (" +
          ryokanPeakNights +
          "p / " +
          ryokanOffpeakNights +
          "o)",
        ""
      ],
      [
        "Gross Annual Booking Revenue",
        fmtDual(minpakuGrossRev),
        fmtDual(ryokanGrossRev),
        ""
      ],
      [
        "Management & OTA Fees (" + mgmtFeePct + "%)",
        "-" + fmtDual(minpakuMgmtCost),
        "-" + fmtDual(ryokanMgmtCost),
        ""
      ],
      [
        "Annual Fixed OpEx & Property Tax",
        "-" + fmtDual(fixedOpexJpy),
        "-" + fmtDual(fixedOpexJpy),
        ""
      ],
      [
        "Net Operating Income (Annual NOI)",
        fmtDual(minpakuNoi),
        fmtDual(ryokanNoi),
        "row-highlight"
      ],
      [
        "Total Capital Basis (incl. Closing & CapEx)",
        fmtDual(basisMinpaku),
        fmtDual(basisRyokan) + " (incl. Fire/Permit)",
        ""
      ],
      [
        "Net Cash-on-Cash Yield (%)",
        yieldMinpaku.toFixed(2) + "%",
        yieldRyokan.toFixed(2) + "%",
        "row-Total"
      ]
    ];

    document.getElementById("ledgerTableBody").innerHTML = rows
      .map(
        (r) =>
          '<tr class="' +
          r[3] +
          '"><td>' +
          escapeHtml(r[0]) +
          "</td><td>" +
          escapeHtml(r[1]) +
          "</td><td>" +
          escapeHtml(r[2]) +
          "</td></tr>"
      )
      .join("");

    renderBilingualBrief();
  }

  function renderBilingualBrief() {
    const resortId = document.getElementById("leadResort").value || state.selectedCalcResortId;
    const resort =
      state.resorts.find((r) => r.id === resortId) || state.resorts[0];
    if (!resort) return "";

    const stage = document.getElementById("leadStage").value;
    const structure = document.getElementById("leadStructure").value;
    const budget = document.getElementById("leadBudget").value;
    const contactName = document.getElementById("leadName").value.trim() || "(Enter buyer name)";
    const contactEmail = document.getElementById("leadEmail").value.trim() || "(Enter buyer email)";
    const parcelNotes = document.getElementById("leadParcelNotes").value.trim();

    const scopes = [];
    if (document.getElementById("chkGyoseishoshi").checked) {
      scopes.push("Gyoseishoshi Zoning & 365d Simple Lodging Permit Pre-Check (旅館業法・簡易宿所事前相談)");
    }
    if (document.getElementById("chkFireVendor").checked) {
      scopes.push("Fire Service Act Jikaho Alarm Quote (消防法令適合通知・自火報見積)");
    }
    if (document.getElementById("chkStrManager").checked) {
      scopes.push("Bilingual STR / Kake-tsuke Management (住宅宿泊管理業者・駆け付け委託)");
    }

    const uw = state.lastUnderwriting;
    const uwLine =
      uw && uw.resort && uw.resort.id === resort.id
        ? "Simulated Basis: " +
          fmtDual(uw.basisRyokan) +
          " | 180d Minpaku NOI: " +
          fmtDual(uw.minpakuNoi) +
          " (" +
          uw.yieldMinpaku.toFixed(2) +
          "%) -> 365d Ryokan NOI: " +
          fmtDual(uw.ryokanNoi) +
          " (" +
          uw.yieldRyokan.toFixed(2) +
          "%)"
        : "Target Municipality Benchmark Price: " +
          fmtDual(resort.benchmark_metrics.typical_price_jpy);

    const briefText = [
      "Pre-Purchase Zoning & 365-Day Ryokan-gyo Inquiry",
      "旅館業（簡易宿所営業）・住宅宿泊事業 事前相談シート",
      "----------------------------------------------------------------------",
      "Prepared via: " + PARTNER_CONFIG.deskDisplayName,
      "Date (UTC):   " + new Date().toISOString().slice(0, 10),
      "",
      "1. Buyer & Property Profile / 買主・検討物件概要",
      "- Contact:          " + contactName + " <" + contactEmail + ">",
      "- Target Market:    " + resort.name + " / " + resort.japanese_name,
      "- Purchase Stage:   " + stage,
      "- Building Type:    " + structure,
      "- Budget Range:     " + budget,
      "- Underwriting:     " + uwLine,
      "",
      "2. Municipal Regulatory Summary / 管轄行政・条例メモ",
      "- Competent Authority: " + resort.ordinance_jurisdiction,
      "- Minpaku Art. 18 Rule: " +
        resort.minpaku_severity +
        " (~" +
        resort.effective_minpaku_days_typical +
        "d/yr)",
      "- 365d Ryokan Viability: " + resort.ryokan_365_feasibility,
      "- Fire & Building Notes: " + resort.fire_safety_and_building_notes,
      "- Official Ordinance URL: " + resort.official_url,
      "",
      "3. Requested Support / 相談希望内容",
      ...(scopes.length
        ? scopes.map((s) => "  - " + s)
        : ["  - General Zoning Consultation"]),
      "",
      "4. Listing URL or Lot Number (Chiban) / 物件URL・地番メモ",
      parcelNotes || "(To be shared upon initial reply)",
      "",
      "5. Japanese Summary for Gyoseishoshi / 行政書士・担当者様向け要約",
      "対象自治体（" +
        resort.japanese_name +
        "）における物件取得前の用途地域・特別用途地区・地区計画の確認、",
      "建築基準法上の用途変更要否（200平米超確認）、消防法（自動火災報知設備・誘導灯）の概算、",
      "ならびに365日営業可能な『旅館業法（簡易宿所営業）』許可取得の可否確認およびお見積りをご相談いたします。"
    ].join("\n");

    document.getElementById("bilingualBriefOutput").textContent = briefText;
    return briefText;
  }

  async function handleLeadSubmit(ev) {
    ev.preventDefault();
    const briefText = renderBilingualBrief();
    const statusEl = document.getElementById("leadStatusMsg");
    statusEl.classList.remove("hidden");

    const resortId = document.getElementById("leadResort").value;
    const resort = state.resorts.find((r) => r.id === resortId) || state.resorts[0];

    if (PARTNER_CONFIG.webhookEndpointUrl) {
      try {
        statusEl.textContent = "Sending inquiry to partner Gyoseishoshi desk...";
        const resp = await fetch(PARTNER_CONFIG.webhookEndpointUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resort: resort.name,
            contactName: document.getElementById("leadName").value,
            contactEmail: document.getElementById("leadEmail").value,
            stage: document.getElementById("leadStage").value,
            structure: document.getElementById("leadStructure").value,
            budget: document.getElementById("leadBudget").value,
            brief: briefText
          })
        });
        if (resp.ok) {
          statusEl.textContent =
            "Request sent. A licensed bilingual Gyoseishoshi partner will reply within 1-2 business days.";
          return;
        }
      } catch (_e) {
        // Fallback to direct intake flow below
      }
    }

    if (PARTNER_CONFIG.partnerBookingUrl) {
      window.open(PARTNER_CONFIG.partnerBookingUrl, "_blank", "noopener,noreferrer");
    }

    const subject = encodeURIComponent(
      "[Pre-Purchase Zoning Check] " + resort.name + " - 365d Ryokan-gyo Feasibility"
    );
    const body = encodeURIComponent(briefText);
    const mailHref =
      "mailto:" + PARTNER_CONFIG.intakeEmail + "?subject=" + subject + "&body=" + body;

    statusEl.innerHTML =
      'Opening email client to <a href="' +
      mailHref +
      '">' +
      escapeHtml(PARTNER_CONFIG.intakeEmail) +
      '</a> with your bilingual consultation sheet (or click "Copy Text").';
    window.location.href = mailHref;
  }

  function wireEvents() {
    document.getElementById("globalFxInput").addEventListener("input", (e) => {
      const val = Number(e.target.value);
      if (val >= 50 && val <= 400) {
        state.fxRate = val;
        renderExplorer();
        calculateYieldComparison();
      }
    });

    ["searchInput", "categorySelect", "severitySelect", "feasibilitySelect", "prefectureSelect"].forEach(
      (id) => {
        document.getElementById(id).addEventListener("input", renderExplorer);
        document.getElementById(id).addEventListener("change", renderExplorer);
      }
    );

    document.getElementById("btnResetFilters").addEventListener("click", () => {
      document.getElementById("searchInput").value = "";
      document.getElementById("categorySelect").value = "ALL";
      document.getElementById("severitySelect").value = "ALL";
      document.getElementById("feasibilitySelect").value = "ALL";
      document.getElementById("prefectureSelect").value = "ALL";
      renderExplorer();
    });

    document.getElementById("btnViewGrid").addEventListener("click", () => {
      state.viewMode = "grid";
      document.getElementById("btnViewGrid").classList.add("active");
      document.getElementById("btnViewTable").classList.remove("active");
      renderExplorer();
    });

    document.getElementById("btnViewTable").addEventListener("click", () => {
      state.viewMode = "table";
      document.getElementById("btnViewTable").classList.add("active");
      document.getElementById("btnViewGrid").classList.remove("active");
      renderExplorer();
    });

    document.getElementById("explorer").addEventListener("click", (e) => {
      const modalBtn = e.target.closest(".js-open-modal");
      if (modalBtn) {
        openModal(modalBtn.getAttribute("data-id"));
        return;
      }
      const calcBtn = e.target.closest(".js-load-calc");
      if (calcBtn) {
        applyResortPresetToCalculator(calcBtn.getAttribute("data-id"), true);
      }
    });

    document.getElementById("btnCloseModal").addEventListener("click", closeModal);
    document.getElementById("ordinanceModal").addEventListener("click", (e) => {
      if (e.target.id === "ordinanceModal") closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });

    document.getElementById("btnModalSimulate").addEventListener("click", () => {
      const id = state.activeModalResortId;
      closeModal();
      if (id) applyResortPresetToCalculator(id, true);
    });

    document.getElementById("btnModalZoningCheck").addEventListener("click", () => {
      const id = state.activeModalResortId;
      closeModal();
      if (id) {
        applyResortPresetToCalculator(id, false);
        document.getElementById("leadResort").value = id;
        renderBilingualBrief();
        document.getElementById("zoning-desk").scrollIntoView({ behavior: "smooth" });
      }
    });

    document.getElementById("calcResortPreset").addEventListener("change", (e) => {
      applyResortPresetToCalculator(e.target.value, false);
    });

    [
      "inpPriceJpy",
      "inpClosingPct",
      "inpRenoJpy",
      "inpFireUpgradeJpy",
      "inpPeakAdrJpy",
      "inpOffpeakAdrJpy",
      "inpPeakMonths",
      "inpMinpakuCapDays",
      "inpPeakOccPct",
      "inpOffpeakOccPct",
      "inpMgmtFeePct",
      "inpFixedOpexJpy"
    ].forEach((id) => {
      document.getElementById(id).addEventListener("input", calculateYieldComparison);
    });

    document.getElementById("btnSendCalcToDesk").addEventListener("click", () => {
      document.getElementById("leadResort").value = state.selectedCalcResortId;
      renderBilingualBrief();
      document.getElementById("zoning-desk").scrollIntoView({ behavior: "smooth" });
    });

    [
      "leadResort",
      "leadStage",
      "leadStructure",
      "leadBudget",
      "leadName",
      "leadEmail",
      "leadParcelNotes",
      "chkGyoseishoshi",
      "chkFireVendor",
      "chkStrManager"
    ].forEach((id) => {
      document.getElementById(id).addEventListener("input", renderBilingualBrief);
      document.getElementById(id).addEventListener("change", renderBilingualBrief);
    });

    document.getElementById("leadForm").addEventListener("submit", handleLeadSubmit);

    document.getElementById("btnCopyBrief").addEventListener("click", async () => {
      const text = renderBilingualBrief();
      const btn = document.getElementById("btnCopyBrief");
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "Copied";
        setTimeout(() => {
          btn.textContent = "Copy Text";
        }, 1800);
      } catch (_err) {
        btn.textContent = "Select Below";
      }
    });

    document.getElementById("btnDownloadBrief").addEventListener("click", () => {
      const text = renderBilingualBrief();
      const resortId = document.getElementById("leadResort").value || "japan-resort";
      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "zoning-due-diligence-" + resortId + ".txt";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  async function init() {
    const dataset = await loadOrdinanceDataset();
    state.resorts = dataset.resorts || [];
    state.summary = dataset.summary || {};

    if (state.summary.total_resorts) {
      document.getElementById("kpiTotalResorts").textContent = String(
        state.summary.total_resorts
      );
    }
    if (state.summary.average_effective_minpaku_cap_days) {
      document.getElementById("kpiAvgMinpakuDays").textContent =
        state.summary.average_effective_minpaku_cap_days + " days/yr";
    }

    populateDropdowns();
    wireEvents();
    renderExplorer();

    const params = new URLSearchParams(window.location.search);
    const marketParam = (params.get("market") || "").trim().toLowerCase();
    const matchedMarket = state.resorts.find((r) => r.id === marketParam);
    const initialId = matchedMarket
      ? matchedMarket.id
      : state.resorts.some((r) => r.id === "hakuba")
      ? "hakuba"
      : state.resorts[0]
      ? state.resorts[0].id
      : "";
    if (initialId) {
      applyResortPresetToCalculator(initialId, Boolean(matchedMarket && !window.location.hash));
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
