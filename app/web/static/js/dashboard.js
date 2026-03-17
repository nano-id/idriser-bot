(function () {
  const REFRESH_INTERVAL_MS = 20000;
  const LANGUAGE_STORAGE_KEY = "idriser_language";
  const SUPPORTED_LANGUAGES = ["en", "tr"];

  const TR = {};

  Object.assign(TR, {
    "sidebar.controlSurface": "Kontrol Yüzeyi",
    "sidebar.versionLabel": "Sürüm {version}",
    "sidebar.language": "Dil",
    "sidebar.main": "Ana Bölüm",
    "nav.dashboard": "Panel",
    "nav.dashboardSub": "Genel görünüm",
    "nav.signals": "Sinyaller",
    "nav.signalsSub": "Piyasa akışı",
    "nav.parameters": "Parametreler",
    "nav.parametersSub": "Strateji ayarları",
    "nav.paper": "Simülasyon",
    "nav.paperSub": "Sanal işlem masası",
    "nav.runtime": "Çalışma",
    "nav.runtimeSub": "Kontroller",
    "page.sectionLabel": "Panel",
    "page.title": "ID-Riser kontrol merkezine hoş geldin",
    "page.subtitle": "Motor sağlığını ve aktif piyasa adaylarını tek teknik panelden izle.",
    "controls.title": "Kontroller",
    "controls.subtitle": "Motor işlemleri",
    "controls.runOnce": "Tek Tur Çalıştır",
    "controls.startEngine": "Motoru Başlat",
    "controls.stopEngine": "Motoru Durdur",
    "controls.startPaperRunner": "Simülasyonu Başlat",
    "controls.stopPaperRunner": "Simülasyonu Durdur",
    "controls.runPaperCycle": "Simülasyon Turu Çalıştır",
    "controls.runHistoricalSimulation": "Tarihsel Simülasyonu Çalıştır",
    "controls.resetPaperPortfolio": "Simülasyon Portföyünü Sıfırla",
    "controls.refresh": "Yenile",
    "controls.pauseAutoRefresh": "Otomatik Yenilemeyi Durdur",
    "kpi.engineState": "Motor Durumu",
    "kpi.activeSignals": "Aktif Sinyaller",
    "kpi.decisionHorizon": "Karar Ufku",
    "overview.signalRadar": "Sinyal Radarı",
    "overview.signalRadarSub": "Son taramadaki en güçlü adaylar",
    "overview.noSignals": "Henüz aktif sinyal yok.",
    "overview.recentActivity": "Son Hareketler",
    "overview.recentActivitySub": "Motor, YZ ve simülasyon katmanlarının operasyon özeti",
    "overview.noActivity": "Henüz son hareket yok.",
    "overview.systemStatus": "Sistem Durumu",
    "overview.systemStatusSub": "Arka uç sağlığı ve çalışma bağlantıları",
    "overview.paperSnapshot": "Simülasyon Özeti",
    "overview.paperSnapshotSub": "Kısa bakiye ve masa görünümü",
    "labels.appVersion": "Uygulama Sürümü",
    "labels.exchange": "Borsa",
    "labels.decisionHorizon": "Karar Ufku",
    "labels.llmProvider": "YZ Sağlayıcı",
    "labels.llmEnabled": "YZ Açık",
    "labels.runtimeOverride": "Çalışma Ayarı",
    "labels.enabled": "Açık",
    "labels.cashBalance": "Nakit Bakiye",
    "labels.openTrades": "Açık İşlemler",
    "labels.closedTrades": "Kapanan İşlemler",
    "labels.realizedPnl": "Gerçekleşen K/Z",
    "labels.unrealizedPnl": "Gerçekleşmemiş K/Z",
  });

  Object.assign(TR, {
    "signals.aggregateTitle": "Son Bileşik Sinyaller",
    "signals.aggregateSub": "Arka uç durumundan gelen son çoklu ufuk bileşik verisi",
    "signals.noAggregate": "Henüz bileşik sinyal yok.",
    "signals.aiTitle": "Son YZ Sinyalleri",
    "signals.aiSub": "Sağlayıcıdan bağımsız destek çıktıları",
    "signals.noAi": "Henüz YZ destek sinyali yok.",
    "parameters.configTitle": "Parametreler",
    "parameters.configSub": "Runtime, motor, YZ ve toplulaştırma ayarlarını tek yerden yönet.",
    "paper.statusTitle": "Simülasyon Durumu",
    "paper.statusSub": "Simülasyon döngüsü, ritim ve masa durumu",
    "paper.controlsTitle": "Simülasyon Kontrolleri",
    "paper.controlsSub": "Elle simülasyon döngüsü işlemleri",
    "paper.portfolioTitle": "Simülasyon Portföyü",
    "paper.portfolioSub": "Sanal bakiye ve K/Z özeti",
    "paper.metricsTitle": "Simülasyon Performansı",
    "paper.metricsSub": "Kazanma oranı, beklenti, drawdown ve işlem kalitesi özeti",
    "paper.openTradesTitle": "Açık İşlemler",
    "paper.openTradesSub": "Aktif simülasyon pozisyonları",
    "paper.noOpenTrades": "Açık simülasyon işlemi yok.",
    "paper.closedTradesTitle": "Kapanan İşlemler",
    "paper.closedTradesSub": "Tamamlanan simülasyon pozisyonları",
    "paper.noClosedTrades": "Kapanan simülasyon işlemi yok.",
    "paper.eventsTitle": "Simülasyon Günlüğü",
    "paper.eventsSub": "Son açma, kapama, tur, sıfırlama ve uyarı olayları",
    "paper.noEvents": "Henüz simülasyon olayı yok.",
    "paper.historicalTitle": "Tarihsel Simülasyon",
    "paper.historicalSub": "Mevcut parametrelerle tek bir sembolü geçmişten geleceğe oynat.",
    "paper.historicalNoteTitle": "Aktif parametre seti kullanılır",
    "paper.historicalNoteSub": "Bu replay, Parametreler sayfasındaki güncel Adım 1, Adım 2, Adım 3 ve Simülasyon ayarlarını kullanır.",
    "paper.noHistoricalResult": "Henüz tarihsel simülasyon sonucu yok.",
    "paper.historicalEvaluationsTitle": "Tarihsel Karar Noktaları",
    "paper.historicalEvaluationsSub": "Seçilen aralıktaki son karar anları ve filtre sonucu.",
    "paper.noHistoricalEvaluations": "Henüz tarihsel değerlendirme yok.",
    "runtime.engineStatusTitle": "Motor Durumu",
    "runtime.engineStatusSub": "Son tarama ritmi, hatalar ve durum sayıları",
    "runtime.controlsTitle": "Motor Kontrolleri",
    "runtime.controlsSub": "Elle tarama ve yenileme işlemleri",
    "runtime.configTitle": "Çalışma Ayarları",
    "runtime.configSub": "Gizli olmayan çalışma kontrollerini güncelle",
    "runtime.saveConfig": "Çalışma Ayarlarını Kaydet",
    "runtime.resetDefaults": "Varsayılanlara Dön",
    "labels.lastRun": "Son Çalıştırma",
    "labels.wins": "Kazanç",
    "labels.losses": "Kayıp",
    "labels.lastError": "Son Hata",
    "labels.equity": "Özsermaye",
    "labels.cash": "Nakit",
    "labels.engineRunning": "Motor Çalışıyor",
    "labels.paperRunner": "Simülasyon Döngüsü",
    "labels.paperRefreshSeconds": "Simülasyon Yenileme",
    "labels.paperSyncEngineBeforeRun": "Tur Öncesi Motor Senkronu",
    "labels.paperOpenedLastCycle": "Son Tur Açılan",
    "labels.paperClosedLastCycle": "Son Tur Kapanan",
    "labels.paperTotalClosedTrades": "Toplam Kapanan",
    "labels.paperWinRate": "Kazanma Oranı",
    "labels.paperExpectancy": "Beklenti",
    "labels.paperProfitFactor": "Kâr Faktörü",
    "labels.paperBestTrade": "En İyi İşlem",
    "labels.paperWorstTrade": "En Kötü İşlem",
    "labels.paperMaxDrawdown": "Maks Drawdown",
    "labels.lastSuccess": "Son Başarılı Çalışma",
    "labels.latestSignals": "Son Sinyaller",
    "labels.latestAiSignals": "Son YZ Sinyalleri",
    "labels.supportedHorizons": "Desteklenen Ufuklar",
    "labels.engineEnabled": "Motor Açık",
    "labels.engineUniverseSize": "Motor Evren Boyutu",
    "labels.engineRefresh": "Motor Yenileme Süresi",
    "labels.includeStep2": "Adım 2 Dahil",
    "labels.includeStep3": "Adım 3 Dahil",
    "labels.includeAiSupport": "YZ Desteği Dahil",
    "labels.engineMaxSignals": "Maksimum Sinyal",
    "labels.snapshotTimeframe": "Snapshot Zaman Dilimi",
    "labels.snapshotInterval": "Snapshot Aralığı",
    "labels.aggregationWindow": "Toplulaştırma Penceresi",
    "labels.minimumSnapshots": "Minimum Görüntü",
    "labels.bullishThreshold": "Yükseliş Eşiği",
    "labels.deepseekEnabled": "DeepSeek Açık",
    "labels.aiShortlistLimit": "YZ Aday Limiti",
    "labels.aiMinimumAggregateScore": "YZ Minimum Bileşik Skoru",
    "labels.deepseekModel": "DeepSeek Modeli",
    "labels.deepseekTimeout": "DeepSeek Zaman Aşımı",
    "labels.geminiModel": "Gemini Modeli",
    "labels.geminiTimeout": "Gemini Zaman Aşımı",
    "labels.runtimePath": "Çalışma Dosyası",
  });

  Object.assign(TR, {
    "table.symbol": "Sembol",
    "table.horizon": "Ufuk",
    "table.meanSignal": "Ortalama Sinyal",
    "table.bullishRatio": "Yükseliş Oranı",
    "table.stability": "İstikrar",
    "table.breakout": "Kırılım",
    "table.windowComplete": "Pencere Tam",
    "table.fallback": "Geri Düşüş",
    "table.step2Score": "Adım 2 Skoru",
    "table.step2Pass": "Adım 2 Geçti",
    "table.regime": "Rejim",
    "table.step3Pass": "Adım 3 Geçti",
    "table.provider": "Sağlayıcı",
    "table.supportScore": "Destek Skoru",
    "table.narrativeStrength": "Anlatı Gücü",
    "table.riskLabel": "Risk Etiketi",
    "table.summary": "Özet",
    "table.tradeId": "İşlem No",
    "table.entry": "Giriş",
    "table.current": "Güncel",
    "table.quantity": "Miktar",
    "table.pnlPct": "K/Z %",
    "table.pnlValue": "K/Z Değeri",
    "table.stop": "Zarar Durdur",
    "table.takeProfit": "Kâr Al",
    "table.openedAt": "Açılış",
    "table.exit": "Çıkış",
    "table.reasonClosed": "Kapanış Nedeni",
    "table.closedAt": "Kapanış",
    "table.eventTime": "Zaman",
    "table.eventType": "Olay Tipi",
    "table.openedTrades": "Açılan",
    "table.closedTradesShort": "Kapanan",
  });

  Object.assign(TR, {
    "parameters.step1Tab": "Adım 1",
    "parameters.step2Tab": "Adım 2",
    "parameters.step3Tab": "Adım 3",
    "parameters.aiTab": "Yapay Zeka",
    "parameters.paperTab": "Simülasyon",
    "parameters.step1DataTitle": "Adım 1 Veri ve Tarama",
    "parameters.step1DataSub": "Evren, snapshot ve toplulaştırma ayarları.",
    "parameters.step1ScoreTitle": "Adım 1 Skor Ağırlıkları",
    "parameters.step1ScoreSub": "Bileşik sinyal bileşen etkileri.",
    "parameters.step2CoreTitle": "Adım 2 Teknik Filtre",
    "parameters.step2CoreSub": "Trend, momentum ve giriş kalitesi ayarları.",
    "parameters.step2WeightsTitle": "Adım 2 Ağırlıkları",
    "parameters.step2WeightsSub": "Teknik skor alt bileşen etkileri.",
    "parameters.step3CoreTitle": "Adım 3 Rejim Filtresi",
    "parameters.step3CoreSub": "BTC rejimi ve veto kuralları.",
    "parameters.step3BreadthTitle": "Adım 3 Breadth Ayarları",
    "parameters.step3BreadthSub": "Piyasa genişliği örneklemesi ve oran eşikleri.",
    "parameters.step3DerivativesTitle": "Adım 3 Türev ve Fallback",
    "parameters.step3DerivativesSub": "Fonlama, nötr skor ve fallback cezası ayarları.",
    "parameters.step3WeightsTitle": "Adım 3 Ağırlıkları",
    "parameters.step3WeightsSub": "Rejim skor alt bileşen etkileri.",
    "parameters.aiCoreTitle": "Yapay Zeka Desteği",
    "parameters.aiCoreSub": "Sağlayıcı, model ve eşik ayarları.",
    "parameters.paperCoreTitle": "Simülasyon Parametreleri",
    "parameters.paperCoreSub": "Paper masa risk ve pozisyon ayarları.",
    "parameters.actionsNote": "Değişiklikler kaydedildikten sonra çalışma yapılandırmasına yazılır.",
    "parameters.overviewTitle": "Bu sayfa nasıl okunur?",
    "parameters.overviewSub": "Adım 1 veri toplama ve bileşik skoru, Adım 2 teknik filtreyi, Adım 3 rejim vetosunu yönetir. Yapay zeka ve simülasyon ana sinyal motorundan ayrı tutulur.",
    "parameters.statusDataFlow": "Veri Akışı",
    "parameters.statusRequiredSnapshots": "Gerekli Snapshot",
    "parameters.statusWeightTotal": "Ağırlık Toplamı",
    "parameters.statusTechnicalFrame": "Teknik Ufuklar",
    "parameters.statusBreakoutRule": "Kırılım Kuralı",
    "parameters.statusRegimeScope": "Rejim Kapsamı",
    "parameters.statusVetoRules": "Veto Kuralları",
    "parameters.statusAiMode": "YZ Modu",
    "parameters.statusAiThreshold": "YZ Eşiği",
    "parameters.statusAiProvider": "Sağlayıcı Ayarı",
    "parameters.statusPaperRisk": "Risk Bütçesi",
    "parameters.statusPaperGate": "İşlem Kapısı",
    "parameters.statusPaperExit": "Çıkış Kuralı",
    "parameters.hintDecisionHorizon": "Trade kararının hangi pencere için üretileceğini belirler.",
    "parameters.hintSupportedHorizons": "Karar ufku sadece bu listedeki değerler arasında seçilebilir.",
    "parameters.hintSnapshotTimeframe": "Ham piyasa verisinin hangi mum boyutuyla toplandığını belirler.",
    "parameters.hintSnapshotInterval": "Motorun veri toplama tekrar aralığı.",
    "parameters.hintAggregationWindow": "Tek bir aggregate karar için saklanan toplam snapshot adedi.",
    "parameters.hintMinimumSnapshots": "Eksik veri halinde geçerli kabul edilen asgari snapshot sayısı.",
    "parameters.hintBullishThreshold": "Aggregate sinyalin yapıcı sayılması için gereken minimum yükseliş oranı.",
    "labels.aggregationWeightTrend": "Trend Ağırlığı",
    "labels.aggregationWeightSlope": "Eğim Ağırlığı",
    "labels.aggregationWeightRsi": "RSI Ağırlığı",
    "labels.aggregationWeightMacd": "MACD Ağırlığı",
    "labels.aggregationWeightAdx": "ADX Ağırlığı",
    "labels.aggregationWeightVolume": "Hacim Ağırlığı",
    "labels.aggregationWeightBreakout": "Kırılım Ağırlığı",
    "labels.aggregationStabilityCap": "İstikrar Kapağı",
    "labels.technicalMainTimeframe": "Ana Zaman Dilimi",
    "labels.technicalConfirmationTimeframe": "Onay Zaman Dilimi",
    "labels.technicalSecondaryConfirmation": "İkincil Onay Kullan",
    "labels.technicalPassThreshold": "Geçiş Eşiği",
    "labels.technicalOhlcvLimit": "OHLCV Limit",
    "labels.technicalMinRows": "Minimum Mum",
    "labels.technicalMaFast": "Hızlı Ortalama",
    "labels.technicalMaSlow": "Yavaş Ortalama",
    "labels.technicalMaSlopeLookback": "Slope Bakış",
    "labels.technicalMaSlopeMinPct": "Slope Alt Eşik",
    "labels.technicalMaSlopeGoodPct": "Slope Güçlü Eşik",
    "labels.technicalAdxPeriod": "ADX Periyodu",
    "labels.technicalAdxMin": "ADX Alt Eşik",
    "labels.technicalAdxStrong": "ADX Güçlü Eşik",
    "labels.technicalRsiPeriod": "RSI Periyodu",
    "labels.technicalRsiMin": "RSI Alt Band",
    "labels.technicalRsiMax": "RSI Üst Band",
    "labels.technicalRsiExtreme": "RSI Aşırı Bölge",
    "labels.technicalMacdFast": "MACD Hızlı",
    "labels.technicalMacdSlow": "MACD Yavaş",
    "labels.technicalMacdSignal": "MACD Sinyal",
    "labels.technicalStochPeriod": "Stoch Periyodu",
    "labels.technicalStochBullishMin": "Stoch Alt Band",
    "labels.technicalStochOverbought": "Stoch Aşırı Bölge",
    "labels.technicalAtrPeriod": "ATR Periyodu",
    "labels.technicalAtrPctMin": "ATR Alt Oran",
    "labels.technicalAtrPctMax": "ATR Üst Oran",
    "labels.technicalBbandsPeriod": "Bollinger Periyodu",
    "labels.technicalBbandsStddev": "Bollinger Std",
    "labels.technicalBbCompressionMax": "Sıkışma Eşiği",
    "labels.technicalBbExpansionMin": "Genişleme Eşiği",
    "labels.technicalOverextendedAboveUpperPct": "Aşırı Uzama Oranı",
    "labels.technicalVolumeMaPeriod": "Hacim Ortalama Periyodu",
    "labels.technicalVolumeRatioMin": "Min Hacim Oranı",
    "labels.technicalVolumeRatioStrong": "Güçlü Hacim Oranı",
    "labels.technicalBreakoutLookback": "Kırılım Bakış",
    "labels.technicalBreakoutBuffer": "Kırılım Buffer",
    "labels.technicalPullbackTolerancePct": "Pullback Toleransı",
    "labels.technicalMissingCriticalPenalty": "Kritik Eksik Ceza",
    "labels.technicalSecondaryConfirmationPenalty": "İkincil Onay Ceza",
    "labels.technicalOverextendedPenalty": "Aşırı Uzama Ceza",
    "labels.technicalNoisyPenalty": "Noisy Yapı Ceza",
    "labels.technicalWeightTrend": "Trend",
    "labels.technicalWeightMomentum": "Momentum",
    "labels.technicalWeightVolatility": "Volatilite",
    "labels.technicalWeightVolume": "Hacim",
    "labels.technicalWeightEntry": "Giriş",
    "labels.technicalCriticalIndicators": "Kritik Göstergeler",
    "labels.regimeBtcSymbol": "BTC Sembolü",
    "labels.regimeTimeframe": "Rejim Zaman Dilimi",
    "labels.regimeOhlcvLimit": "OHLCV Limit",
    "labels.regimeMinRows": "Minimum Mum",
    "labels.regimeBtcMaFast": "BTC Hızlı Ortalama",
    "labels.regimeBtcMaSlow": "BTC Yavaş Ortalama",
    "labels.regimeBtcSlopeLookback": "BTC Slope Bakış",
    "labels.regimeBtcSlopeMinPct": "BTC Slope Alt Eşik",
    "labels.regimeBtcSlopeGoodPct": "BTC Slope Güçlü Eşik",
    "labels.regimeAdxPeriod": "ADX Periyodu",
    "labels.regimeAdxMin": "ADX Alt Eşik",
    "labels.regimeAdxStrong": "ADX Güçlü Eşik",
    "labels.regimeAtrPeriod": "ATR Periyodu",
    "labels.regimeBreadthEnabled": "Piyasa Genişliği",
    "labels.regimeBreadthTimeframe": "Breadth Zaman Dilimi",
    "labels.regimeBreadthSymbolCount": "Breadth Sembol Sayısı",
    "labels.regimeBreadthMinSamples": "Breadth Minimum Örnek",
    "labels.regimeBreadthFastPeriod": "Breadth Hızlı Ortalama",
    "labels.regimeBreadthSlowPeriod": "Breadth Yavaş Ortalama",
    "labels.regimeBreadthBullishRatio": "Breadth Boğa Oranı",
    "labels.regimeBreadthBearishRatio": "Breadth Ayı Oranı",
    "labels.regimeDerivativesEnabled": "Türev Verisi",
    "labels.regimeDerivativesSymbol": "Türev Sembolü",
    "labels.regimeFundingAbsMax": "Fonlama Üst Sınırı",
    "labels.regimeDerivativesNeutralScore": "Türev Nötr Skoru",
    "labels.regimeFallbackPenaltyPoints": "Fallback Ceza Puanı",
    "labels.regimeAtrDanger": "ATR Tehlike Eşiği",
    "labels.regimeDrawdownLookback": "Drawdown Bakış",
    "labels.regimeDrawdownDanger": "Drawdown Tehlike Eşiği",
    "labels.regimeBullishThreshold": "Boğa Eşiği",
    "labels.regimeNeutralThreshold": "Nötr Eşiği",
    "labels.regimeAllowNeutral": "Nötr Rejime İzin Ver",
    "labels.regimeVetoBearish": "Ayıda Veto",
    "labels.regimeVetoDanger": "Tehlikede Veto",
    "labels.regimeWeightTrend": "Trend",
    "labels.regimeWeightVolatility": "Volatilite",
    "labels.regimeWeightBreadth": "Genişlik",
    "labels.regimeWeightDerivatives": "Türev",
    "labels.paperEnabled": "Simülasyon Açık",
    "labels.paperInitialCapital": "Başlangıç Sermayesi",
    "labels.paperMaxOpenPositions": "Maks Açık Pozisyon",
    "labels.paperRiskPerTrade": "İşlem Başına Risk",
    "labels.paperMinSignalScore": "Min Sinyal Skoru",
    "labels.paperRequireStep2": "Step2 Geçişi Zorunlu",
    "labels.paperRequireStep3": "Step3 Geçişi Zorunlu",
    "labels.paperRequireWindowComplete": "Tam Pencere Zorunlu",
    "labels.paperAtrStopMultiplier": "ATR Stop Çarpanı",
    "labels.paperRiskRewardRatio": "Risk / Getiri",
    "labels.paperMaxHoldMinutes": "Maks Bekleme Dakikası",
    "labels.historicalSymbol": "Sembol",
    "labels.historicalStartAt": "Başlangıç Tarihi",
    "labels.historicalEndAt": "Bitiş Tarihi",
    "labels.historicalForceClose": "Açık işlemleri sonda kapat",
    "labels.historicalResultSymbol": "Sonuç Sembolü",
    "labels.historicalRange": "Aralık",
    "labels.historicalFinalEquity": "Final Özsermaye",
    "labels.historicalReturnPct": "Getiri %",
    "labels.historicalOpenedTrades": "Açılan İşlem",
    "labels.historicalClosedTrades": "Kapanan İşlem",
    "labels.historicalSelectedSignals": "Seçilen Sinyal",
    "labels.historicalEvaluations": "Değerlendirme",
    "labels.historicalNetProfit": "Net Kar/Zarar",
    "labels.historicalMaxDrawdown": "Maks Drawdown",
    "labels.historicalWinRate": "Kazanma Oranı",
    "labels.historicalWarnings": "Uyarı",
  });

  const MSG_EN = {
    unknown: "unknown",
    enabled: "enabled",
    disabled: "disabled",
    configured: "configured",
    missingKey: "missing key",
    present: "present",
    default: "default",
    running: "running",
    stopped: "stopped",
    yes: "yes",
    no: "no",
    complete: "complete",
    incomplete: "incomplete",
    autoRefreshEvery: "Auto refresh every {seconds}s",
    autoRefreshPaused: "Auto refresh paused",
    lastUpdatedNever: "Last updated: never",
    lastUpdatedAt: "Last updated: {time}",
    refreshing: "Refreshing dashboard data...",
    updated: "Dashboard updated.",
    refreshFailed: "Refresh failed: {error}",
    runtimeUpdated: "Runtime config updated.",
    runtimeUpdateFailed: "Runtime config update failed.",
    runtimeReset: "Runtime config reset to defaults.",
    runtimeResetFailed: "Runtime reset failed: {error}",
    engineRunStarted: "Engine run_once started...",
    engineRunCompleted: "Engine run_once completed.",
    engineRunFailed: "Engine run_once failed: {error}",
    engineStarted: "Engine started.",
    engineStartFailed: "Engine start failed: {error}",
    engineStopped: "Engine stopped.",
    engineStopFailed: "Engine stop failed: {error}",
    paperStarted: "Simulation started.",
    paperStartFailed: "Simulation start failed: {error}",
    paperStopped: "Simulation stopped.",
    paperStopFailed: "Simulation stop failed: {error}",
    paperRunCompleted: "Paper cycle completed.",
    paperRunFailed: "Paper cycle failed: {error}",
    paperReset: "Paper portfolio reset.",
    paperResetFailed: "Paper reset failed: {error}",
    historicalStarted: "Historical simulation started...",
    historicalCompleted: "Historical simulation completed.",
    historicalFailed: "Historical simulation failed: {error}",
    historicalMissingFields: "Symbol, start date, and end date are required.",
    autoRefreshPausedBanner: "Auto refresh paused.",
    autoRefreshResumedBanner: "Auto refresh resumed.",
    runtimeOverrideActive: "Runtime override active",
    runtimeDefault: "Runtime default",
    llmChip: "AI {provider}",
    horizonChip: "Horizon {horizon}",
    openTrades: "{count} open trades",
    parameterFlow: "{base} -> {horizon}",
    parameterWindow: "{required} required | min {minimum}",
    parameterWeights: "{value}",
    parameterFrames: "{main} main | {confirm} confirm",
    parameterBreakout: "{lookback} bars | {buffer}% buffer",
    parameterRegime: "{symbol} | {timeframe}",
    parameterVeto: "bearish {bearish} | danger {danger}",
    parameterAiMode: "{provider} | {enabled}",
    parameterAiThreshold: "{limit} shortlist | min {score}",
    parameterAiProvider: "{provider} settings",
    parameterPaperRisk: "{risk}% x {positions} = {budget}%",
    parameterPaperGate: "score {score} | final {final} | step2 {step2} | step3 {step3}",
    parameterPaperExit: "ATR x{atr} | RR {rr} | {minutes}m | {refresh}s | fee {fee}bps | slip {slip}bps",
    signalHorizon: "{horizon} horizon",
    step2: "Step2 {score}",
    regimePending: "regime pending",
    engineActive: "Engine loop active",
    engineWaiting: "Engine waiting",
    lastIssue: "Last issue: {error}",
    latestScanCount: "Latest scan count: {count}",
    topSignal: "Top signal: {symbol}",
    topSignalDetail: "Score {score} | {regime}",
    aiSupportFrom: "AI support from {provider}",
    aiNoteAvailable: "AI note available",
    providerConfigured: "Provider configured",
    providerMissing: "Provider key missing or disabled",
    paperDeskEnabled: "Simulation desk enabled",
    paperDeskDisabled: "Simulation desk disabled",
    paperDeskDetail: "{open} open / {closed} closed trades",
    pauseAutoRefresh: "Pause Auto Refresh",
    resumeAutoRefresh: "Resume Auto Refresh",
  };

  const MSG_TR = {
    unknown: "bilinmiyor",
    enabled: "açık",
    disabled: "kapalı",
    configured: "hazır",
    missingKey: "anahtar eksik",
    present: "var",
    default: "varsayılan",
    running: "çalışıyor",
    stopped: "durdu",
    yes: "evet",
    no: "hayır",
    complete: "tam",
    incomplete: "eksik",
    autoRefreshEvery: "Otomatik yenileme: {seconds} sn",
    autoRefreshPaused: "Otomatik yenileme durdu",
    lastUpdatedNever: "Son güncelleme: hiç",
    lastUpdatedAt: "Son güncelleme: {time}",
    refreshing: "Panel verileri yenileniyor...",
    updated: "Panel güncellendi.",
    refreshFailed: "Yenileme başarısız: {error}",
    runtimeUpdated: "Çalışma ayarları güncellendi.",
    runtimeUpdateFailed: "Çalışma ayarları güncellenemedi.",
    runtimeReset: "Çalışma ayarları varsayılanlara döndü.",
    runtimeResetFailed: "Çalışma ayarları sıfırlanamadı: {error}",
    engineRunStarted: "Motor tek tur çalıştırılıyor...",
    engineRunCompleted: "Motor tek tur çalıştırıldı.",
    engineRunFailed: "Motor tek tur çalıştırılamadı: {error}",
    engineStarted: "Motor başlatıldı.",
    engineStartFailed: "Motor başlatılamadı: {error}",
    engineStopped: "Motor durduruldu.",
    engineStopFailed: "Motor durdurulamadı: {error}",
    paperStarted: "Simülasyon başlatıldı.",
    paperStartFailed: "Simülasyon başlatılamadı: {error}",
    paperStopped: "Simülasyon durduruldu.",
    paperStopFailed: "Simülasyon durdurulamadı: {error}",
    paperRunCompleted: "Simülasyon turu tamamlandı.",
    paperRunFailed: "Simülasyon turu başarısız: {error}",
    paperReset: "Simülasyon portföyü sıfırlandı.",
    paperResetFailed: "Simülasyon sıfırlanamadı: {error}",
    historicalStarted: "Tarihsel simülasyon başlatıldı...",
    historicalCompleted: "Tarihsel simülasyon tamamlandı.",
    historicalFailed: "Tarihsel simülasyon başarısız: {error}",
    historicalMissingFields: "Sembol, başlangıç tarihi ve bitiş tarihi zorunlu.",
    autoRefreshPausedBanner: "Otomatik yenileme durduruldu.",
    autoRefreshResumedBanner: "Otomatik yenileme yeniden başladı.",
    runtimeOverrideActive: "Özel çalışma ayarı aktif",
    runtimeDefault: "Varsayılan çalışma ayarı",
    llmChip: "YZ {provider}",
    horizonChip: "Ufuk {horizon}",
    openTrades: "{count} açık işlem",
    parameterFlow: "{base} -> {horizon}",
    parameterWindow: "{required} gerekli | min {minimum}",
    parameterWeights: "{value}",
    parameterFrames: "ana {main} | onay {confirm}",
    parameterBreakout: "{lookback} mum | %{buffer} tampon",
    parameterRegime: "{symbol} | {timeframe}",
    parameterVeto: "ayı {bearish} | tehlike {danger}",
    parameterAiMode: "{provider} | {enabled}",
    parameterAiThreshold: "{limit} shortlist | min {score}",
    parameterAiProvider: "{provider} ayarları",
    parameterPaperRisk: "%{risk} x {positions} = %{budget}",
    parameterPaperGate: "skor {score} | final {final} | step2 {step2} | step3 {step3}",
    parameterPaperExit: "ATR x{atr} | RR {rr} | {minutes} dk | {refresh} sn | komisyon {fee}bps | kayma {slip}bps",
    signalHorizon: "{horizon} ufku",
    step2: "Adım 2 {score}",
    regimePending: "rejim bekleniyor",
    engineActive: "Motor döngüsü aktif",
    engineWaiting: "Motor beklemede",
    lastIssue: "Son sorun: {error}",
    latestScanCount: "Son tarama sayısı: {count}",
    topSignal: "En güçlü sinyal: {symbol}",
    topSignalDetail: "Skor {score} | {regime}",
    aiSupportFrom: "YZ desteği: {provider}",
    aiNoteAvailable: "YZ notu hazır",
    providerConfigured: "Sağlayıcı hazır",
    providerMissing: "Sağlayıcı anahtarı eksik veya kapalı",
    paperDeskEnabled: "Simülasyon masası açık",
    paperDeskDisabled: "Simülasyon masası kapalı",
    paperDeskDetail: "{open} açık / {closed} kapanan işlem",
    pauseAutoRefresh: "Otomatik Yenilemeyi Durdur",
    resumeAutoRefresh: "Otomatik Yenilemeyi Sürdür",
  };

  const state = {
    refreshEnabled: true,
    refreshTimer: null,
    llmProvider: "unknown",
    language: getInitialLanguage(),
    lastUpdatedAt: null,
    banner: null,
    latestPayloads: null,
  };

  const elements = {
    tabButtons: Array.from(document.querySelectorAll("[data-tab-target]")),
    tabPanels: Array.from(document.querySelectorAll(".tab-panel")),
    parameterSectionButtons: Array.from(document.querySelectorAll("[data-parameter-section-target]")),
    parameterPanels: Array.from(document.querySelectorAll(".parameter-panel")),
    banner: document.getElementById("feedback-banner"),
    lastUpdated: document.getElementById("last-updated"),
    refreshMeta: document.getElementById("refresh-meta"),
    refreshNowBtn: document.getElementById("refresh-now-btn"),
    toggleRefreshBtn: document.getElementById("toggle-refresh-btn"),
    engineRunOnceBtn: document.getElementById("engine-run-once-btn"),
    engineStartBtn: document.getElementById("engine-start-btn"),
    engineStopBtn: document.getElementById("engine-stop-btn"),
    paperStartBtn: document.getElementById("paper-start-btn"),
    paperStopBtn: document.getElementById("paper-stop-btn"),
    paperRunOnceBtn: document.getElementById("paper-run-once-btn"),
    paperResetBtn: document.getElementById("paper-reset-btn"),
    historicalRunBtn: document.getElementById("historical-run-btn"),
    runtimeForm: document.getElementById("runtime-config-form"),
    runtimeResetBtn: document.getElementById("runtime-reset-btn"),
    runtimeError: document.getElementById("runtime-form-error"),
    languageSelector: document.getElementById("language-selector"),
    historicalFormError: document.getElementById("historical-form-error"),
    aggregateBody: document.getElementById("aggregate-signals-body"),
    aggregateEmpty: document.getElementById("aggregate-empty-state"),
    aiBody: document.getElementById("ai-signals-body"),
    aiEmpty: document.getElementById("ai-empty-state"),
    openTradesBody: document.getElementById("paper-open-trades-body"),
    openTradesEmpty: document.getElementById("paper-open-empty-state"),
    closedTradesBody: document.getElementById("paper-closed-trades-body"),
    closedTradesEmpty: document.getElementById("paper-closed-empty-state"),
    paperEventsBody: document.getElementById("paper-events-body"),
    paperEventsEmpty: document.getElementById("paper-events-empty-state"),
    historicalEvaluationsBody: document.getElementById("historical-evaluations-body"),
    historicalEvaluationsEmpty: document.getElementById("historical-evaluations-empty-state"),
    overview: {
      llmProvider: document.getElementById("overview-llm-provider"),
      decisionHorizon: document.getElementById("overview-decision-horizon"),
      runtimeOverride: document.getElementById("overview-runtime-override"),
      signalList: document.getElementById("overview-signal-list"),
      signalEmpty: document.getElementById("overview-signal-empty"),
      activityList: document.getElementById("overview-activity-list"),
      activityEmpty: document.getElementById("overview-activity-empty"),
    },
    hero: {
      engineState: document.getElementById("hero-engine-state"),
      signalCount: document.getElementById("hero-signal-count"),
      decisionHorizon: document.getElementById("hero-decision-horizon"),
      aiCount: document.getElementById("hero-ai-count"),
      equity: document.getElementById("hero-equity"),
      openTrades: document.getElementById("hero-open-trades"),
    },
    engine: {
      running: document.getElementById("engine-running"),
      lastRun: document.getElementById("engine-last-run"),
      lastRunDetail: document.getElementById("engine-last-run-detail"),
      lastSuccess: document.getElementById("engine-last-success"),
      signalCount: document.getElementById("engine-signal-count"),
      aiSignalCount: document.getElementById("engine-ai-signal-count"),
      lastError: document.getElementById("engine-last-error"),
    },
    paper: {
      running: document.getElementById("paper-running"),
      enabled: document.getElementById("paper-enabled"),
      lastRun: document.getElementById("paper-last-run"),
      lastSuccess: document.getElementById("paper-last-success"),
      lastError: document.getElementById("paper-last-error"),
      refreshSeconds: document.getElementById("paper-refresh-seconds"),
      syncEngineBeforeRun: document.getElementById("paper-sync-engine-before-run"),
      lastOpenedCount: document.getElementById("paper-last-opened-count"),
      lastClosedCount: document.getElementById("paper-last-closed-count"),
      openCount: document.getElementById("paper-open-count"),
      closedCount: document.getElementById("paper-closed-count"),
      cashBalance: document.getElementById("paper-cash-balance"),
      cashBalanceDetail: document.getElementById("paper-cash-balance-detail"),
      equity: document.getElementById("paper-equity"),
      realizedPnl: document.getElementById("paper-realized-pnl"),
      realizedPnlDetail: document.getElementById("paper-realized-pnl-detail"),
      unrealizedPnl: document.getElementById("paper-unrealized-pnl"),
      unrealizedPnlDetail: document.getElementById("paper-unrealized-pnl-detail"),
      winCount: document.getElementById("paper-win-count"),
      lossCount: document.getElementById("paper-loss-count"),
      metricsTotalClosed: document.getElementById("paper-metrics-total-closed"),
      metricsWinRate: document.getElementById("paper-metrics-win-rate"),
      metricsExpectancy: document.getElementById("paper-metrics-expectancy"),
      metricsProfitFactor: document.getElementById("paper-metrics-profit-factor"),
      metricsBestTrade: document.getElementById("paper-metrics-best-trade"),
      metricsWorstTrade: document.getElementById("paper-metrics-worst-trade"),
      metricsMaxDrawdown: document.getElementById("paper-metrics-max-drawdown"),
    },
    historical: {
      symbol: document.getElementById("historical-symbol"),
      startAt: document.getElementById("historical-start-at"),
      endAt: document.getElementById("historical-end-at"),
      closeOpen: document.getElementById("historical-close-open"),
      empty: document.getElementById("historical-empty-state"),
      resultSymbol: document.getElementById("historical-result-symbol"),
      range: document.getElementById("historical-result-range"),
      finalEquity: document.getElementById("historical-result-final-equity"),
      returnPct: document.getElementById("historical-result-return-pct"),
      openedTrades: document.getElementById("historical-result-opened-trades"),
      closedTrades: document.getElementById("historical-result-closed-trades"),
      selectedSignals: document.getElementById("historical-result-selected-signals"),
      evaluations: document.getElementById("historical-result-evaluations"),
      netProfit: document.getElementById("historical-result-net-profit"),
      maxDrawdown: document.getElementById("historical-result-max-drawdown"),
      winRate: document.getElementById("historical-result-win-rate"),
      warningCount: document.getElementById("historical-result-warning-count"),
    },
    system: {
      appVersion: document.getElementById("status-app-version"),
      exchangeId: document.getElementById("status-exchange-id"),
      decisionHorizon: document.getElementById("status-decision-horizon"),
      llmProvider: document.getElementById("status-llm-provider"),
      llmEnabled: document.getElementById("status-llm-enabled"),
      llmConfigured: document.getElementById("status-llm-configured"),
      runtimeOverride: document.getElementById("status-runtime-override"),
      runtimePath: document.getElementById("status-runtime-path"),
    },
    parameterSummary: {
      horizon: document.getElementById("parameter-summary-horizon"),
      snapshot: document.getElementById("parameter-summary-snapshot"),
      step2: document.getElementById("parameter-summary-step2"),
      step3: document.getElementById("parameter-summary-step3"),
      ai: document.getElementById("parameter-summary-ai"),
      paper: document.getElementById("parameter-summary-paper"),
    },
    parameterStatus: {
      step1Flow: document.getElementById("parameter-step1-flow"),
      step1Window: document.getElementById("parameter-step1-window"),
      step1Weights: document.getElementById("parameter-step1-weights"),
      step2Frames: document.getElementById("parameter-step2-frames"),
      step2Breakout: document.getElementById("parameter-step2-breakout"),
      step2Weights: document.getElementById("parameter-step2-weights"),
      step3Scope: document.getElementById("parameter-step3-scope"),
      step3Veto: document.getElementById("parameter-step3-veto"),
      step3Weights: document.getElementById("parameter-step3-weights"),
      aiMode: document.getElementById("parameter-ai-mode"),
      aiThreshold: document.getElementById("parameter-ai-threshold"),
      aiProviderNote: document.getElementById("parameter-ai-provider-note"),
      paperRisk: document.getElementById("parameter-paper-risk"),
      paperGate: document.getElementById("parameter-paper-gate"),
      paperExit: document.getElementById("parameter-paper-exit"),
    },
    providerBlocks: Array.from(document.querySelectorAll("[data-provider-block]")),
    config: {
      decisionHorizon: document.getElementById("cfg-decision-horizon"),
      supportedHorizons: document.getElementById("cfg-supported-horizons"),
      engineEnabled: document.getElementById("cfg-engine-enabled"),
      engineUniverseSize: document.getElementById("cfg-engine-universe-size"),
      engineRefreshSeconds: document.getElementById("cfg-engine-refresh-seconds"),
      engineIncludeStep2: document.getElementById("cfg-engine-include-step2"),
      engineIncludeStep3: document.getElementById("cfg-engine-include-step3"),
      engineIncludeAiSupport: document.getElementById("cfg-engine-include-ai-support"),
      engineMaxSignals: document.getElementById("cfg-engine-max-signals"),
      snapshotTimeframe: document.getElementById("cfg-snapshot-timeframe"),
      snapshotIntervalMinutes: document.getElementById("cfg-snapshot-interval-minutes"),
      hourlyWindow: document.getElementById("cfg-hourly-window"),
      hourlyMinSnapshots: document.getElementById("cfg-hourly-min-snapshots"),
      aggregationThreshold: document.getElementById("cfg-aggregation-threshold"),
      aggregationWeightTrend: document.getElementById("cfg-aggregation-weight-trend"),
      aggregationWeightSlope: document.getElementById("cfg-aggregation-weight-slope"),
      aggregationWeightRsi: document.getElementById("cfg-aggregation-weight-rsi"),
      aggregationWeightMacd: document.getElementById("cfg-aggregation-weight-macd"),
      aggregationWeightAdx: document.getElementById("cfg-aggregation-weight-adx"),
      aggregationWeightVolume: document.getElementById("cfg-aggregation-weight-volume"),
      aggregationWeightBreakout: document.getElementById("cfg-aggregation-weight-breakout"),
      aggregationStabilityCap: document.getElementById("cfg-aggregation-stability-cap"),
      technicalMainTimeframe: document.getElementById("cfg-technical-main-timeframe"),
      technicalConfirmationTimeframe: document.getElementById("cfg-technical-confirmation-timeframe"),
      technicalSecondaryConfirmation: document.getElementById("cfg-technical-secondary-confirmation"),
      technicalPassThreshold: document.getElementById("cfg-technical-pass-threshold"),
      technicalOhlcvLimit: document.getElementById("cfg-technical-ohlcv-limit"),
      technicalMinOhlcvRows: document.getElementById("cfg-technical-min-ohlcv-rows"),
      technicalMaFast: document.getElementById("cfg-technical-ma-fast"),
      technicalMaSlow: document.getElementById("cfg-technical-ma-slow"),
      technicalMaSlopeLookback: document.getElementById("cfg-technical-ma-slope-lookback"),
      technicalMaSlopeMinPct: document.getElementById("cfg-technical-ma-slope-min-pct"),
      technicalMaSlopeGoodPct: document.getElementById("cfg-technical-ma-slope-good-pct"),
      technicalAdxPeriod: document.getElementById("cfg-technical-adx-period"),
      technicalAdxMin: document.getElementById("cfg-technical-adx-min"),
      technicalAdxStrong: document.getElementById("cfg-technical-adx-strong"),
      technicalRsiPeriod: document.getElementById("cfg-technical-rsi-period"),
      technicalRsiMin: document.getElementById("cfg-technical-rsi-min"),
      technicalRsiMax: document.getElementById("cfg-technical-rsi-max"),
      technicalRsiExtreme: document.getElementById("cfg-technical-rsi-extreme"),
      technicalMacdFast: document.getElementById("cfg-technical-macd-fast"),
      technicalMacdSlow: document.getElementById("cfg-technical-macd-slow"),
      technicalMacdSignal: document.getElementById("cfg-technical-macd-signal"),
      technicalStochPeriod: document.getElementById("cfg-technical-stoch-period"),
      technicalStochBullishMin: document.getElementById("cfg-technical-stoch-bullish-min"),
      technicalStochOverbought: document.getElementById("cfg-technical-stoch-overbought"),
      technicalAtrPeriod: document.getElementById("cfg-technical-atr-period"),
      technicalAtrPctMin: document.getElementById("cfg-technical-atr-pct-min"),
      technicalAtrPctMax: document.getElementById("cfg-technical-atr-pct-max"),
      technicalBbandsPeriod: document.getElementById("cfg-technical-bbands-period"),
      technicalBbandsStddev: document.getElementById("cfg-technical-bbands-stddev"),
      technicalBbWidthCompressionMax: document.getElementById("cfg-technical-bb-width-compression-max"),
      technicalBbWidthExpansionMin: document.getElementById("cfg-technical-bb-width-expansion-min"),
      technicalOverextendedAboveUpperPct: document.getElementById("cfg-technical-overextended-above-upper-pct"),
      technicalVolumeMaPeriod: document.getElementById("cfg-technical-volume-ma-period"),
      technicalVolumeRatioMin: document.getElementById("cfg-technical-volume-ratio-min"),
      technicalVolumeRatioStrong: document.getElementById("cfg-technical-volume-ratio-strong"),
      technicalBreakoutLookback: document.getElementById("cfg-technical-breakout-lookback"),
      technicalBreakoutBuffer: document.getElementById("cfg-technical-breakout-buffer"),
      technicalPullbackTolerancePct: document.getElementById("cfg-technical-pullback-tolerance-pct"),
      technicalMissingCriticalPenalty: document.getElementById("cfg-technical-missing-critical-penalty"),
      technicalSecondaryConfirmationPenalty: document.getElementById("cfg-technical-secondary-confirmation-penalty"),
      technicalOverextendedPenalty: document.getElementById("cfg-technical-overextended-penalty"),
      technicalNoisyPenalty: document.getElementById("cfg-technical-noisy-penalty"),
      technicalWeightTrend: document.getElementById("cfg-technical-weight-trend"),
      technicalWeightMomentum: document.getElementById("cfg-technical-weight-momentum"),
      technicalWeightVolatility: document.getElementById("cfg-technical-weight-volatility"),
      technicalWeightVolume: document.getElementById("cfg-technical-weight-volume"),
      technicalWeightEntry: document.getElementById("cfg-technical-weight-entry"),
      technicalCriticalIndicators: document.getElementById("cfg-technical-critical-indicators"),
      regimeBtcSymbol: document.getElementById("cfg-regime-btc-symbol"),
      regimeTimeframe: document.getElementById("cfg-regime-timeframe"),
      regimeOhlcvLimit: document.getElementById("cfg-regime-ohlcv-limit"),
      regimeMinOhlcvRows: document.getElementById("cfg-regime-min-ohlcv-rows"),
      regimeBtcMaFast: document.getElementById("cfg-regime-btc-ma-fast"),
      regimeBtcMaSlow: document.getElementById("cfg-regime-btc-ma-slow"),
      regimeBtcSlopeLookback: document.getElementById("cfg-regime-btc-slope-lookback"),
      regimeBtcSlopeMinPct: document.getElementById("cfg-regime-btc-slope-min-pct"),
      regimeBtcSlopeGoodPct: document.getElementById("cfg-regime-btc-slope-good-pct"),
      regimeAdxPeriod: document.getElementById("cfg-regime-adx-period"),
      regimeAdxMin: document.getElementById("cfg-regime-adx-min"),
      regimeAdxStrong: document.getElementById("cfg-regime-adx-strong"),
      regimeAtrPeriod: document.getElementById("cfg-regime-atr-period"),
      regimeBreadthEnabled: document.getElementById("cfg-regime-breadth-enabled"),
      regimeBreadthTimeframe: document.getElementById("cfg-regime-breadth-timeframe"),
      regimeBreadthSymbolCount: document.getElementById("cfg-regime-breadth-symbol-count"),
      regimeBreadthMinSamples: document.getElementById("cfg-regime-breadth-min-samples"),
      regimeBreadthFastPeriod: document.getElementById("cfg-regime-breadth-fast-period"),
      regimeBreadthSlowPeriod: document.getElementById("cfg-regime-breadth-slow-period"),
      regimeBreadthBullishRatio: document.getElementById("cfg-regime-breadth-bullish-ratio"),
      regimeBreadthBearishRatio: document.getElementById("cfg-regime-breadth-bearish-ratio"),
      regimeDerivativesEnabled: document.getElementById("cfg-regime-derivatives-enabled"),
      regimeDerivativesSymbol: document.getElementById("cfg-regime-derivatives-symbol"),
      regimeFundingAbsMax: document.getElementById("cfg-regime-funding-abs-max"),
      regimeDerivativesNeutralScore: document.getElementById("cfg-regime-derivatives-neutral-score"),
      regimeFallbackPenaltyPoints: document.getElementById("cfg-regime-fallback-penalty-points"),
      regimeAtrDanger: document.getElementById("cfg-regime-atr-danger"),
      regimeDrawdownLookback: document.getElementById("cfg-regime-drawdown-lookback"),
      regimeDrawdownDanger: document.getElementById("cfg-regime-drawdown-danger"),
      regimeBullishThreshold: document.getElementById("cfg-regime-bullish-threshold"),
      regimeNeutralThreshold: document.getElementById("cfg-regime-neutral-threshold"),
      regimeAllowNeutral: document.getElementById("cfg-regime-allow-neutral"),
      regimeVetoBearish: document.getElementById("cfg-regime-veto-bearish"),
      regimeVetoDanger: document.getElementById("cfg-regime-veto-danger"),
      regimeWeightTrend: document.getElementById("cfg-regime-weight-trend"),
      regimeWeightVolatility: document.getElementById("cfg-regime-weight-volatility"),
      regimeWeightBreadth: document.getElementById("cfg-regime-weight-breadth"),
      regimeWeightDerivatives: document.getElementById("cfg-regime-weight-derivatives"),
      deepseekEnabled: document.getElementById("cfg-deepseek-enabled"),
      llmProvider: document.getElementById("cfg-llm-provider"),
      deepseekShortlistLimit: document.getElementById("cfg-deepseek-shortlist-limit"),
      deepseekMinAggregateScore: document.getElementById("cfg-deepseek-min-aggregate-score"),
      deepseekModel: document.getElementById("cfg-deepseek-model"),
      deepseekTimeoutSeconds: document.getElementById("cfg-deepseek-timeout-seconds"),
      geminiModel: document.getElementById("cfg-gemini-model"),
      geminiTimeoutSeconds: document.getElementById("cfg-gemini-timeout-seconds"),
      paperEnabled: document.getElementById("cfg-paper-enabled"),
      paperInitialCapital: document.getElementById("cfg-paper-initial-capital"),
      paperMaxOpenPositions: document.getElementById("cfg-paper-max-open-positions"),
      paperRiskPerTradePct: document.getElementById("cfg-paper-risk-per-trade-pct"),
      paperMinSignalScore: document.getElementById("cfg-paper-min-signal-score"),
      paperRequireFinalSelected: document.getElementById("cfg-paper-require-final-selected"),
      paperRequireStep2Pass: document.getElementById("cfg-paper-require-step2-pass"),
      paperRequireStep3Pass: document.getElementById("cfg-paper-require-step3-pass"),
      paperRequireWindowComplete: document.getElementById("cfg-paper-require-window-complete"),
      paperAtrStopMultiplier: document.getElementById("cfg-paper-atr-stop-multiplier"),
      paperRiskRewardRatio: document.getElementById("cfg-paper-risk-reward-ratio"),
      paperMaxHoldMinutes: document.getElementById("cfg-paper-max-hold-minutes"),
      paperFeeBps: document.getElementById("cfg-paper-fee-bps"),
      paperSlippageBps: document.getElementById("cfg-paper-slippage-bps"),
      paperRefreshSeconds: document.getElementById("cfg-paper-refresh-seconds"),
      paperSyncEngineBeforeRun: document.getElementById("cfg-paper-sync-engine-before-run"),
    },
  };

  function getInitialLanguage() {
    try {
      const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (SUPPORTED_LANGUAGES.includes(stored)) {
        return stored;
      }
    } catch {
      // ignore localStorage errors
    }
    return navigator.language && navigator.language.toLowerCase().startsWith("tr") ? "tr" : "en";
  }

  function msg(key, args = {}, fallback = key) {
    const dictionary = state.language === "tr" ? MSG_TR : MSG_EN;
    let template = dictionary[key] || fallback;
    Object.entries(args).forEach(([name, value]) => {
      template = template.replaceAll(`{${name}}`, String(value ?? ""));
    });
    return template;
  }

  function translateStatic(key, args = {}, fallback = key) {
    let template = state.language === "tr" ? (TR[key] || fallback) : fallback;
    Object.entries(args).forEach(([name, value]) => {
      template = template.replaceAll(`{${name}}`, String(value ?? ""));
    });
    return template;
  }

  function parseI18nArgs(raw) {
    if (!raw) {
      return {};
    }
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
      return {};
    }
  }

  function applyTranslations() {
    document.documentElement.lang = state.language;
    if (elements.languageSelector) {
      elements.languageSelector.value = state.language;
    }
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.dataset.i18n;
      const fallback = node.dataset.defaultText || node.textContent || key;
      if (!node.dataset.defaultText) {
        node.dataset.defaultText = fallback;
      }
      node.textContent = translateStatic(key, parseI18nArgs(node.dataset.i18nArgs), fallback);
    });
    updateRefreshUi();
    updateLastUpdatedLabel();
    renderBanner();
  }

  function setLanguage(language) {
    if (!SUPPORTED_LANGUAGES.includes(language)) {
      return;
    }
    state.language = language;
    try {
      window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    } catch {
      // ignore localStorage errors
    }
    applyTranslations();
    rerenderFromState();
  }

  function setBanner(key, type, args = {}) {
    state.banner = { key, type, args };
    renderBanner();
  }

  function renderBanner() {
    if (!elements.banner) {
      return;
    }
    if (!state.banner) {
      elements.banner.classList.add("hidden");
      elements.banner.textContent = "";
      elements.banner.classList.remove("feedback-info", "feedback-success", "feedback-error");
      return;
    }
    elements.banner.textContent = msg(state.banner.key, state.banner.args);
    elements.banner.classList.remove("hidden", "feedback-info", "feedback-success", "feedback-error");
    elements.banner.classList.add(
      state.banner.type === "success"
        ? "feedback-success"
        : state.banner.type === "error"
          ? "feedback-error"
          : "feedback-info",
    );
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    if (!response.ok) {
      const detail = payload && payload.detail ? payload.detail : `Request failed (${response.status})`;
      throw new Error(formatErrorDetail(detail));
    }
    return payload;
  }

  function formatErrorDetail(detail) {
    if (Array.isArray(detail)) {
      return detail.map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object" && item.msg) {
          return String(item.msg);
        }
        return JSON.stringify(item);
      }).join(" | ");
    }
    if (typeof detail === "object" && detail !== null) {
      return JSON.stringify(detail);
    }
    return String(detail);
  }

  function getLocale() {
    return state.language === "tr" ? "tr-TR" : "en-US";
  }

  function formatNumber(value, digits = 4) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "-";
    }
    return new Intl.NumberFormat(getLocale(), {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(value);
  }

  function formatInteger(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "0";
    }
    return new Intl.NumberFormat(getLocale(), { maximumFractionDigits: 0 }).format(value);
  }

  function formatDateTime(value) {
    if (!value) {
      return "-";
    }
    const dt = new Date(value);
    if (Number.isNaN(dt.getTime())) {
      return String(value);
    }
    return new Intl.DateTimeFormat(getLocale(), { dateStyle: "short", timeStyle: "short" }).format(dt);
  }

  function toDatetimeLocalValue(value) {
    const dt = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(dt.getTime())) {
      return "";
    }
    const year = dt.getFullYear();
    const month = String(dt.getMonth() + 1).padStart(2, "0");
    const day = String(dt.getDate()).padStart(2, "0");
    const hours = String(dt.getHours()).padStart(2, "0");
    const minutes = String(dt.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  function formatTimeOnly(value) {
    const dt = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(dt.getTime())) {
      return "-";
    }
    return new Intl.DateTimeFormat(getLocale(), {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(dt);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll("\"", "&quot;")
      .replaceAll("'", "&#039;");
  }

  function renderBooleanBadge(value, trueText, falseText, trueClass = "badge-enabled", falseClass = "badge-warning") {
    if (value === true) {
      return `<span class="badge ${trueClass}">${escapeHtml(trueText)}</span>`;
    }
    if (value === false) {
      return `<span class="badge ${falseClass}">${escapeHtml(falseText)}</span>`;
    }
    return "-";
  }

  function renderFinalStatusBadge(row) {
    if (row.final_selected === true) {
      return `<span class="badge badge-enabled">${escapeHtml(state.language === "tr" ? "AKTIF" : "ACTIVE")}</span>`;
    }
    if (row.final_selected === false) {
      return `<span class="badge badge-warning">${escapeHtml(state.language === "tr" ? "VETO" : "VETO")}</span>`;
    }
    return `<span class="badge badge-neutral">${escapeHtml(msg("unknown"))}</span>`;
  }

  function renderRejectStageBadge(row) {
    const stage = row.reject_stage || "NONE";
    if (stage === "NONE") {
      return `<span class="badge badge-enabled">${escapeHtml(state.language === "tr" ? "GECTI" : "PASSED")}</span>`;
    }
    if (stage === "STEP2") {
      return `<span class="badge badge-warning">${escapeHtml(state.language === "tr" ? "ADIM 2" : "STEP2")}</span>`;
    }
    if (stage === "STEP3") {
      return `<span class="badge badge-warning">${escapeHtml(state.language === "tr" ? "ADIM 3" : "STEP3")}</span>`;
    }
    return `<span class="badge badge-neutral">${escapeHtml(stage)}</span>`;
  }

  function setBadge(element, value, trueText, falseText) {
    if (!element) {
      return;
    }
    element.classList.remove("badge-enabled", "badge-disabled", "badge-neutral");
    element.classList.add("badge");
    if (value === true) {
      element.textContent = trueText;
      element.classList.add("badge-enabled");
      return;
    }
    if (value === false) {
      element.textContent = falseText;
      element.classList.add("badge-disabled");
      return;
    }
    element.textContent = msg("unknown");
    element.classList.add("badge-neutral");
  }

  function activateTab(targetId) {
    elements.tabButtons.forEach((button) => {
      const active = button.dataset.tabTarget === targetId;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });
    elements.tabPanels.forEach((panel) => {
      const active = panel.id === targetId;
      panel.classList.toggle("active", active);
      panel.setAttribute("aria-hidden", active ? "false" : "true");
    });
  }

  function activateParameterSection(targetId) {
    elements.parameterSectionButtons.forEach((button) => {
      const active = button.dataset.parameterSectionTarget === targetId;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });
    elements.parameterPanels.forEach((panel) => {
      const active = panel.id === targetId;
      panel.classList.toggle("active", active);
      panel.setAttribute("aria-hidden", active ? "false" : "true");
    });
  }

  function syncDecisionHorizonOptions(supportedHorizons, selectedHorizon) {
    const select = elements.config.decisionHorizon;
    if (!select) {
      return;
    }
    const horizons = Array.isArray(supportedHorizons) && supportedHorizons.length
      ? supportedHorizons
      : ["5m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "8h", "12h", "1d"];
    const existing = Array.from(select.options).map((option) => option.value);
    if (JSON.stringify(existing) !== JSON.stringify(horizons)) {
      select.innerHTML = "";
      horizons.forEach((horizon) => {
        const option = document.createElement("option");
        option.value = horizon;
        option.textContent = horizon;
        select.appendChild(option);
      });
    }
    select.value = horizons.includes(selectedHorizon) ? selectedHorizon : horizons[0];
  }

  function syncStaticTimeframeOptions(selectElement, selectedValue) {
    if (!selectElement) {
      return;
    }
    const options = ["1m", "5m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "8h", "12h", "1d"];
    const existing = Array.from(selectElement.options).map((option) => option.value);
    if (JSON.stringify(existing) !== JSON.stringify(options)) {
      selectElement.innerHTML = "";
      options.forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        selectElement.appendChild(option);
      });
    }
    selectElement.value = options.includes(selectedValue) ? selectedValue : options[0];
  }

  function timeframeToMinutes(value) {
    const match = /^(\d+)([mhd])$/i.exec(String(value || "").trim());
    if (!match) {
      return null;
    }
    const amount = Number.parseInt(match[1], 10);
    const unit = match[2].toLowerCase();
    if (unit === "m") {
      return amount;
    }
    if (unit === "h") {
      return amount * 60;
    }
    if (unit === "d") {
      return amount * 1440;
    }
    return null;
  }

  function readNumberValue(element) {
    if (!element) {
      return null;
    }
    const value = Number.parseFloat(element.value);
    return Number.isFinite(value) ? value : null;
  }

  function readIntegerValue(element) {
    if (!element) {
      return null;
    }
    const value = Number.parseInt(element.value, 10);
    return Number.isFinite(value) ? value : null;
  }

  function sumValues(values) {
    return values.reduce((total, value) => total + (Number.isFinite(value) ? value : 0), 0);
  }

  function setStatusValue(element, text, tone = "neutral") {
    if (!element) {
      return;
    }
    element.textContent = text;
    element.classList.remove("status-tone-ok", "status-tone-warn", "status-tone-danger", "status-tone-neutral");
    element.classList.add(
      tone === "ok"
        ? "status-tone-ok"
        : tone === "warn"
          ? "status-tone-warn"
          : tone === "danger"
            ? "status-tone-danger"
            : "status-tone-neutral",
    );
  }

  function updateProviderBlocks(provider) {
    elements.providerBlocks.forEach((block) => {
      const blockProvider = block.dataset.providerBlock;
      const active = provider !== "disabled" && blockProvider === provider;
      block.classList.toggle("hidden", provider === "disabled" ? true : !active);
      block.classList.toggle("is-muted", provider !== "disabled" && !active);
    });
  }

  function renderSupportedHorizons(horizons) {
    const container = elements.config.supportedHorizons;
    if (!container) {
      return;
    }
    container.innerHTML = "";
    const values = Array.isArray(horizons) ? horizons : [];
    values.forEach((horizon) => {
      const chip = document.createElement("span");
      chip.className = "inline-chip";
      chip.textContent = horizon;
      container.appendChild(chip);
    });
  }

  function renderParameterSummary(cfg) {
    if (!cfg) {
      return;
    }
    if (elements.parameterSummary.horizon) {
      elements.parameterSummary.horizon.textContent = cfg.decision_horizon || "-";
    }
    if (elements.parameterSummary.snapshot) {
      elements.parameterSummary.snapshot.textContent = `${cfg.snapshot_timeframe || "-"} / ${cfg.snapshot_interval_minutes ?? "-"}`;
    }
    setBadge(elements.parameterSummary.step2, cfg.engine_include_step2, msg("enabled"), msg("disabled"));
    setBadge(elements.parameterSummary.step3, cfg.engine_include_step3, msg("enabled"), msg("disabled"));
    if (elements.parameterSummary.ai) {
      elements.parameterSummary.ai.textContent = cfg.llm_provider || "-";
    }
    setBadge(elements.parameterSummary.paper, cfg.paper_bot_enabled, msg("enabled"), msg("disabled"));
  }

  function renderParameterDiagnostics(cfg) {
    if (!cfg) {
      return;
    }

    const horizonMinutes = timeframeToMinutes(cfg.decision_horizon);
    const snapshotInterval = Number.isFinite(cfg.snapshot_interval_minutes) ? cfg.snapshot_interval_minutes : null;
    const requiredSnapshots = horizonMinutes && snapshotInterval ? Math.max(1, Math.ceil(horizonMinutes / snapshotInterval)) : null;

    setStatusValue(
      elements.parameterStatus.step1Flow,
      msg("parameterFlow", {
        base: cfg.snapshot_timeframe || "-",
        horizon: cfg.decision_horizon || "-",
      }),
      "neutral",
    );
    setStatusValue(
      elements.parameterStatus.step1Window,
      msg("parameterWindow", {
        required: requiredSnapshots ?? "-",
        minimum: cfg.hourly_min_snapshots ?? "-",
      }),
      requiredSnapshots !== null && cfg.hourly_min_snapshots >= requiredSnapshots ? "ok" : "warn",
    );

    const step1WeightTotal = sumValues([
      cfg.aggregation_weight_trend,
      cfg.aggregation_weight_slope,
      cfg.aggregation_weight_rsi,
      cfg.aggregation_weight_macd,
      cfg.aggregation_weight_adx,
      cfg.aggregation_weight_volume,
      cfg.aggregation_weight_breakout,
    ]);
    setStatusValue(
      elements.parameterStatus.step1Weights,
      msg("parameterWeights", { value: formatNumber(step1WeightTotal, 2) }),
      step1WeightTotal >= 0.99 && step1WeightTotal <= 1.01 ? "ok" : "warn",
    );

    setStatusValue(
      elements.parameterStatus.step2Frames,
      msg("parameterFrames", {
        main: cfg.technical_main_timeframe || "-",
        confirm: cfg.technical_confirmation_timeframe || "-",
      }),
      cfg.engine_include_step2 ? "ok" : "neutral",
    );
    setStatusValue(
      elements.parameterStatus.step2Breakout,
      msg("parameterBreakout", {
        lookback: cfg.technical_breakout_lookback ?? "-",
        buffer: formatNumber((cfg.technical_breakout_buffer_pct ?? 0) * 100, 2),
      }),
      "neutral",
    );
    const step2WeightTotal = sumValues([
      cfg.technical_weight_trend,
      cfg.technical_weight_momentum,
      cfg.technical_weight_volatility,
      cfg.technical_weight_volume,
      cfg.technical_weight_entry,
    ]);
    setStatusValue(
      elements.parameterStatus.step2Weights,
      msg("parameterWeights", { value: formatNumber(step2WeightTotal, 2) }),
      step2WeightTotal >= 0.99 && step2WeightTotal <= 1.01 ? "ok" : "warn",
    );

    setStatusValue(
      elements.parameterStatus.step3Scope,
      msg("parameterRegime", {
        symbol: cfg.regime_btc_symbol || "-",
        timeframe: cfg.regime_timeframe || "-",
      }),
      cfg.engine_include_step3 ? "ok" : "neutral",
    );
    setStatusValue(
      elements.parameterStatus.step3Veto,
      msg("parameterVeto", {
        bearish: cfg.regime_veto_if_bearish ? msg("enabled") : msg("disabled"),
        danger: cfg.regime_veto_if_danger ? msg("enabled") : msg("disabled"),
      }),
      cfg.regime_veto_if_bearish || cfg.regime_veto_if_danger ? "ok" : "warn",
    );
    const step3WeightTotal = sumValues([
      cfg.regime_weight_trend,
      cfg.regime_weight_volatility,
      cfg.regime_weight_breadth,
      cfg.regime_weight_derivatives,
    ]);
    setStatusValue(
      elements.parameterStatus.step3Weights,
      msg("parameterWeights", { value: formatNumber(step3WeightTotal, 2) }),
      step3WeightTotal >= 0.99 && step3WeightTotal <= 1.01 ? "ok" : "warn",
    );

    setStatusValue(
      elements.parameterStatus.aiMode,
      msg("parameterAiMode", {
        provider: cfg.llm_provider || "disabled",
        enabled: cfg.engine_include_ai_support ? msg("enabled") : msg("disabled"),
      }),
      cfg.engine_include_ai_support ? "ok" : "neutral",
    );
    setStatusValue(
      elements.parameterStatus.aiThreshold,
      msg("parameterAiThreshold", {
        limit: cfg.deepseek_shortlist_limit ?? "-",
        score: formatNumber(cfg.deepseek_min_aggregate_score, 2),
      }),
      "neutral",
    );
    setStatusValue(
      elements.parameterStatus.aiProviderNote,
      msg("parameterAiProvider", { provider: cfg.llm_provider || "disabled" }),
      cfg.llm_provider && cfg.llm_provider !== "disabled" ? "ok" : "warn",
    );

    const totalRiskBudget = (cfg.paper_risk_per_trade_pct ?? 0) * (cfg.paper_max_open_positions ?? 0) * 100;
    setStatusValue(
      elements.parameterStatus.paperRisk,
      msg("parameterPaperRisk", {
        risk: formatNumber((cfg.paper_risk_per_trade_pct ?? 0) * 100, 1),
        positions: cfg.paper_max_open_positions ?? "-",
        budget: formatNumber(totalRiskBudget, 1),
      }),
      totalRiskBudget <= 100 ? "ok" : "danger",
    );
    setStatusValue(
      elements.parameterStatus.paperGate,
      msg("parameterPaperGate", {
        score: formatNumber(cfg.paper_min_signal_score, 2),
        final: cfg.paper_require_final_selected ? msg("yes") : msg("no"),
        step2: cfg.paper_require_step2_pass ? msg("yes") : msg("no"),
        step3: cfg.paper_require_step3_pass ? msg("yes") : msg("no"),
      }),
      cfg.paper_bot_enabled ? "ok" : "neutral",
    );
    setStatusValue(
      elements.parameterStatus.paperExit,
      msg("parameterPaperExit", {
        atr: formatNumber(cfg.paper_atr_stop_multiplier, 1),
        rr: formatNumber(cfg.paper_risk_reward_ratio, 1),
        minutes: cfg.paper_max_hold_minutes ?? "-",
        refresh: cfg.paper_refresh_seconds ?? "-",
        fee: formatNumber(cfg.paper_fee_bps, 1),
        slip: formatNumber(cfg.paper_slippage_bps, 1),
      }),
      "neutral",
    );

    updateProviderBlocks(cfg.llm_provider || "disabled");
  }

  function buildDraftConfig() {
    return {
      snapshot_timeframe: elements.config.snapshotTimeframe?.value || "",
      snapshot_interval_minutes: readIntegerValue(elements.config.snapshotIntervalMinutes),
      hourly_min_snapshots: readIntegerValue(elements.config.hourlyMinSnapshots),
      decision_horizon: elements.config.decisionHorizon?.value || "",
      aggregation_weight_trend: readNumberValue(elements.config.aggregationWeightTrend),
      aggregation_weight_slope: readNumberValue(elements.config.aggregationWeightSlope),
      aggregation_weight_rsi: readNumberValue(elements.config.aggregationWeightRsi),
      aggregation_weight_macd: readNumberValue(elements.config.aggregationWeightMacd),
      aggregation_weight_adx: readNumberValue(elements.config.aggregationWeightAdx),
      aggregation_weight_volume: readNumberValue(elements.config.aggregationWeightVolume),
      aggregation_weight_breakout: readNumberValue(elements.config.aggregationWeightBreakout),
      engine_include_step2: elements.config.engineIncludeStep2?.checked || false,
      technical_main_timeframe: elements.config.technicalMainTimeframe?.value || "",
      technical_confirmation_timeframe: elements.config.technicalConfirmationTimeframe?.value || "",
      technical_use_secondary_confirmation: elements.config.technicalSecondaryConfirmation?.checked || false,
      technical_pass_threshold: readNumberValue(elements.config.technicalPassThreshold),
      technical_ohlcv_limit: readIntegerValue(elements.config.technicalOhlcvLimit),
      technical_min_ohlcv_rows: readIntegerValue(elements.config.technicalMinOhlcvRows),
      technical_ma_fast_period: readIntegerValue(elements.config.technicalMaFast),
      technical_ma_slow_period: readIntegerValue(elements.config.technicalMaSlow),
      technical_ma_slope_lookback: readIntegerValue(elements.config.technicalMaSlopeLookback),
      technical_ma_slope_min_pct: readNumberValue(elements.config.technicalMaSlopeMinPct),
      technical_ma_slope_good_pct: readNumberValue(elements.config.technicalMaSlopeGoodPct),
      technical_adx_period: readIntegerValue(elements.config.technicalAdxPeriod),
      technical_adx_min: readNumberValue(elements.config.technicalAdxMin),
      technical_adx_strong: readNumberValue(elements.config.technicalAdxStrong),
      technical_rsi_period: readIntegerValue(elements.config.technicalRsiPeriod),
      technical_rsi_bullish_min: readNumberValue(elements.config.technicalRsiMin),
      technical_rsi_bullish_max: readNumberValue(elements.config.technicalRsiMax),
      technical_rsi_extreme: readNumberValue(elements.config.technicalRsiExtreme),
      technical_macd_fast: readIntegerValue(elements.config.technicalMacdFast),
      technical_macd_slow: readIntegerValue(elements.config.technicalMacdSlow),
      technical_macd_signal: readIntegerValue(elements.config.technicalMacdSignal),
      technical_stoch_period: readIntegerValue(elements.config.technicalStochPeriod),
      technical_stoch_bullish_min: readNumberValue(elements.config.technicalStochBullishMin),
      technical_stoch_overbought: readNumberValue(elements.config.technicalStochOverbought),
      technical_atr_period: readIntegerValue(elements.config.technicalAtrPeriod),
      technical_atr_pct_min: readNumberValue(elements.config.technicalAtrPctMin),
      technical_atr_pct_max: readNumberValue(elements.config.technicalAtrPctMax),
      technical_bbands_period: readIntegerValue(elements.config.technicalBbandsPeriod),
      technical_bbands_stddev: readNumberValue(elements.config.technicalBbandsStddev),
      technical_bb_width_compression_max: readNumberValue(elements.config.technicalBbWidthCompressionMax),
      technical_bb_width_expansion_min: readNumberValue(elements.config.technicalBbWidthExpansionMin),
      technical_overextended_above_upper_pct: readNumberValue(elements.config.technicalOverextendedAboveUpperPct),
      technical_volume_ma_period: readIntegerValue(elements.config.technicalVolumeMaPeriod),
      technical_breakout_lookback: readIntegerValue(elements.config.technicalBreakoutLookback),
      technical_breakout_buffer_pct: readNumberValue(elements.config.technicalBreakoutBuffer),
      technical_pullback_tolerance_pct: readNumberValue(elements.config.technicalPullbackTolerancePct),
      technical_missing_critical_penalty: readNumberValue(elements.config.technicalMissingCriticalPenalty),
      technical_secondary_confirmation_penalty: readNumberValue(elements.config.technicalSecondaryConfirmationPenalty),
      technical_overextended_penalty: readNumberValue(elements.config.technicalOverextendedPenalty),
      technical_noisy_penalty: readNumberValue(elements.config.technicalNoisyPenalty),
      technical_weight_trend: readNumberValue(elements.config.technicalWeightTrend),
      technical_weight_momentum: readNumberValue(elements.config.technicalWeightMomentum),
      technical_weight_volatility: readNumberValue(elements.config.technicalWeightVolatility),
      technical_weight_volume: readNumberValue(elements.config.technicalWeightVolume),
      technical_weight_entry: readNumberValue(elements.config.technicalWeightEntry),
      technical_critical_indicators: (elements.config.technicalCriticalIndicators?.value || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      engine_include_step3: elements.config.engineIncludeStep3?.checked || false,
      regime_btc_symbol: elements.config.regimeBtcSymbol?.value || "",
      regime_timeframe: elements.config.regimeTimeframe?.value || "",
      regime_ohlcv_limit: readIntegerValue(elements.config.regimeOhlcvLimit),
      regime_min_ohlcv_rows: readIntegerValue(elements.config.regimeMinOhlcvRows),
      regime_btc_ma_fast_period: readIntegerValue(elements.config.regimeBtcMaFast),
      regime_btc_ma_slow_period: readIntegerValue(elements.config.regimeBtcMaSlow),
      regime_btc_slope_lookback: readIntegerValue(elements.config.regimeBtcSlopeLookback),
      regime_btc_slope_min_pct: readNumberValue(elements.config.regimeBtcSlopeMinPct),
      regime_btc_slope_good_pct: readNumberValue(elements.config.regimeBtcSlopeGoodPct),
      regime_adx_period: readIntegerValue(elements.config.regimeAdxPeriod),
      regime_adx_min: readNumberValue(elements.config.regimeAdxMin),
      regime_adx_strong: readNumberValue(elements.config.regimeAdxStrong),
      regime_atr_period: readIntegerValue(elements.config.regimeAtrPeriod),
      regime_veto_if_bearish: elements.config.regimeVetoBearish?.checked || false,
      regime_veto_if_danger: elements.config.regimeVetoDanger?.checked || false,
      regime_breadth_enabled: elements.config.regimeBreadthEnabled?.checked || false,
      regime_breadth_timeframe: elements.config.regimeBreadthTimeframe?.value || "",
      regime_breadth_symbol_count: readIntegerValue(elements.config.regimeBreadthSymbolCount),
      regime_breadth_min_samples: readIntegerValue(elements.config.regimeBreadthMinSamples),
      regime_breadth_fast_period: readIntegerValue(elements.config.regimeBreadthFastPeriod),
      regime_breadth_slow_period: readIntegerValue(elements.config.regimeBreadthSlowPeriod),
      regime_breadth_bullish_ratio: readNumberValue(elements.config.regimeBreadthBullishRatio),
      regime_breadth_bearish_ratio: readNumberValue(elements.config.regimeBreadthBearishRatio),
      regime_derivatives_enabled: elements.config.regimeDerivativesEnabled?.checked || false,
      regime_derivatives_symbol: elements.config.regimeDerivativesSymbol?.value || "",
      regime_funding_abs_max: readNumberValue(elements.config.regimeFundingAbsMax),
      regime_derivatives_neutral_score: readNumberValue(elements.config.regimeDerivativesNeutralScore),
      regime_fallback_penalty_points: readNumberValue(elements.config.regimeFallbackPenaltyPoints),
      regime_drawdown_lookback: readIntegerValue(elements.config.regimeDrawdownLookback),
      regime_weight_trend: readNumberValue(elements.config.regimeWeightTrend),
      regime_weight_volatility: readNumberValue(elements.config.regimeWeightVolatility),
      regime_weight_breadth: readNumberValue(elements.config.regimeWeightBreadth),
      regime_weight_derivatives: readNumberValue(elements.config.regimeWeightDerivatives),
      llm_provider: elements.config.llmProvider?.value || "disabled",
      engine_include_ai_support: elements.config.engineIncludeAiSupport?.checked || false,
      deepseek_shortlist_limit: readIntegerValue(elements.config.deepseekShortlistLimit),
      deepseek_min_aggregate_score: readNumberValue(elements.config.deepseekMinAggregateScore),
      paper_bot_enabled: elements.config.paperEnabled?.checked || false,
      paper_risk_per_trade_pct: readNumberValue(elements.config.paperRiskPerTradePct),
      paper_max_open_positions: readIntegerValue(elements.config.paperMaxOpenPositions),
      paper_min_signal_score: readNumberValue(elements.config.paperMinSignalScore),
      paper_require_final_selected: elements.config.paperRequireFinalSelected?.checked || false,
      paper_require_step2_pass: elements.config.paperRequireStep2Pass?.checked || false,
      paper_require_step3_pass: elements.config.paperRequireStep3Pass?.checked || false,
      paper_atr_stop_multiplier: readNumberValue(elements.config.paperAtrStopMultiplier),
      paper_risk_reward_ratio: readNumberValue(elements.config.paperRiskRewardRatio),
      paper_max_hold_minutes: readIntegerValue(elements.config.paperMaxHoldMinutes),
      paper_fee_bps: readNumberValue(elements.config.paperFeeBps),
      paper_slippage_bps: readNumberValue(elements.config.paperSlippageBps),
      paper_refresh_seconds: readIntegerValue(elements.config.paperRefreshSeconds),
      paper_sync_engine_before_run: elements.config.paperSyncEngineBeforeRun?.checked || false,
    };
  }

  function updateRefreshUi() {
    if (elements.toggleRefreshBtn) {
      elements.toggleRefreshBtn.textContent = state.refreshEnabled ? msg("pauseAutoRefresh") : msg("resumeAutoRefresh");
    }
    if (elements.refreshMeta) {
      elements.refreshMeta.textContent = state.refreshEnabled
        ? msg("autoRefreshEvery", { seconds: Math.round(REFRESH_INTERVAL_MS / 1000) })
        : msg("autoRefreshPaused");
    }
  }

  function updateLastUpdatedLabel() {
    if (!elements.lastUpdated) {
      return;
    }
    elements.lastUpdated.textContent = state.lastUpdatedAt
      ? msg("lastUpdatedAt", { time: formatTimeOnly(state.lastUpdatedAt) })
      : msg("lastUpdatedNever");
  }

  function renderSystemStatus(data) {
    if (elements.system.appVersion) {
      elements.system.appVersion.textContent = data.app_version || "-";
    }
    if (elements.system.exchangeId) {
      elements.system.exchangeId.textContent = data.exchange_id || "-";
    }
    if (elements.system.decisionHorizon) {
      elements.system.decisionHorizon.textContent = data.decision_horizon || "-";
    }
    if (elements.system.llmProvider) {
      elements.system.llmProvider.textContent = data.llm_provider || "-";
    }
    if (elements.system.runtimePath) {
      elements.system.runtimePath.textContent = data.runtime_config_path || "-";
    }
    if (elements.overview.decisionHorizon) {
      elements.overview.decisionHorizon.textContent = msg("horizonChip", { horizon: data.decision_horizon || "-" });
    }
    if (elements.overview.llmProvider) {
      elements.overview.llmProvider.textContent = msg("llmChip", { provider: data.llm_provider || "-" });
    }
    if (elements.hero.decisionHorizon) {
      elements.hero.decisionHorizon.textContent = msg("horizonChip", { horizon: data.decision_horizon || "-" });
    }
    state.llmProvider = data.llm_provider || "unknown";
    setBadge(elements.system.llmEnabled, data.llm_enabled, msg("enabled"), msg("disabled"));
    setBadge(elements.system.llmConfigured, data.llm_configured, msg("configured"), msg("missingKey"));
    setBadge(elements.system.runtimeOverride, data.runtime_override_exists, msg("present"), msg("default"));
    if (elements.overview.runtimeOverride) {
      elements.overview.runtimeOverride.textContent = data.runtime_override_exists ? msg("runtimeOverrideActive") : msg("runtimeDefault");
    }
  }

  function renderEngineStatus(data) {
    setBadge(elements.engine.running, data.running, msg("running"), msg("stopped"));
    const lastRun = formatDateTime(data.last_run_at);
    if (elements.engine.lastRun) {
      elements.engine.lastRun.textContent = lastRun;
    }
    if (elements.engine.lastRunDetail) {
      elements.engine.lastRunDetail.textContent = lastRun;
    }
    if (elements.engine.lastSuccess) {
      elements.engine.lastSuccess.textContent = formatDateTime(data.last_success_at);
    }
    if (elements.engine.signalCount) {
      elements.engine.signalCount.textContent = formatInteger(data.latest_signal_count ?? 0);
    }
    if (elements.engine.aiSignalCount) {
      elements.engine.aiSignalCount.textContent = formatInteger(data.latest_ai_signal_count ?? 0);
    }
    if (elements.engine.lastError) {
      elements.engine.lastError.textContent = data.last_error || "-";
    }
    if (elements.hero.engineState) {
      elements.hero.engineState.textContent = data.running ? msg("running") : msg("stopped");
    }
    if (elements.hero.signalCount) {
      elements.hero.signalCount.textContent = formatInteger(data.latest_signal_count ?? 0);
    }
    if (elements.hero.aiCount) {
      elements.hero.aiCount.textContent = formatInteger(data.latest_ai_signal_count ?? 0);
    }
  }

  function renderPaperStatus(data) {
    setBadge(elements.paper.running, data.running, msg("running"), msg("stopped"));
    setBadge(elements.paper.enabled, data.enabled, msg("enabled"), msg("disabled"));
    elements.paper.lastRun.textContent = formatDateTime(data.last_run_at);
    if (elements.paper.lastSuccess) {
      elements.paper.lastSuccess.textContent = formatDateTime(data.last_success_at);
    }
    if (elements.paper.refreshSeconds) {
      elements.paper.refreshSeconds.textContent = `${formatInteger(data.refresh_seconds ?? 0)}s`;
    }
    setBadge(
      elements.paper.syncEngineBeforeRun,
      data.sync_engine_before_run,
      msg("enabled"),
      msg("disabled"),
    );
    if (elements.paper.lastOpenedCount) {
      elements.paper.lastOpenedCount.textContent = formatInteger(data.last_opened_count ?? 0);
    }
    if (elements.paper.lastClosedCount) {
      elements.paper.lastClosedCount.textContent = formatInteger(data.last_closed_count ?? 0);
    }
    elements.paper.lastError.textContent = data.last_error || "-";
    if (elements.paper.openCount) {
      elements.paper.openCount.textContent = formatInteger(data.open_trade_count ?? 0);
    }
    if (elements.paper.closedCount) {
      elements.paper.closedCount.textContent = formatInteger(data.closed_trade_count ?? 0);
    }
    if (elements.paper.cashBalance) {
      elements.paper.cashBalance.textContent = formatNumber(data.cash_balance, 4);
    }
    elements.paper.cashBalanceDetail.textContent = formatNumber(data.cash_balance, 4);
    elements.paper.equity.textContent = formatNumber(data.equity, 4);
    if (elements.paper.realizedPnl) {
      elements.paper.realizedPnl.textContent = formatNumber(data.realized_pnl, 4);
    }
    elements.paper.realizedPnlDetail.textContent = formatNumber(data.realized_pnl, 4);
    if (elements.paper.unrealizedPnl) {
      elements.paper.unrealizedPnl.textContent = formatNumber(data.unrealized_pnl, 4);
    }
    elements.paper.unrealizedPnlDetail.textContent = formatNumber(data.unrealized_pnl, 4);
    if (elements.hero.openTrades) {
      elements.hero.openTrades.textContent = msg("openTrades", { count: formatInteger(data.open_trade_count ?? 0) });
    }
  }

  function renderPaperMetrics(payload) {
    const metrics = payload.metrics || {};
    if (elements.paper.metricsTotalClosed) {
      elements.paper.metricsTotalClosed.textContent = formatInteger(metrics.total_closed_trades ?? 0);
    }
    elements.paper.winCount.textContent = formatInteger(metrics.win_count ?? 0);
    elements.paper.lossCount.textContent = formatInteger(metrics.loss_count ?? 0);
    if (elements.paper.metricsWinRate) {
      elements.paper.metricsWinRate.textContent = `${formatNumber(metrics.win_rate_pct ?? 0, 1)}%`;
    }
    if (elements.paper.metricsExpectancy) {
      elements.paper.metricsExpectancy.textContent = formatNumber(metrics.expectancy_value, 4);
    }
    if (elements.paper.metricsProfitFactor) {
      elements.paper.metricsProfitFactor.textContent =
        metrics.profit_factor === null || metrics.profit_factor === undefined
          ? "-"
          : formatNumber(metrics.profit_factor, 2);
    }
    if (elements.paper.metricsBestTrade) {
      elements.paper.metricsBestTrade.textContent = `${formatNumber(metrics.best_trade_pct ?? 0, 2)}%`;
    }
    if (elements.paper.metricsWorstTrade) {
      elements.paper.metricsWorstTrade.textContent = `${formatNumber(metrics.worst_trade_pct ?? 0, 2)}%`;
    }
    if (elements.paper.metricsMaxDrawdown) {
      elements.paper.metricsMaxDrawdown.textContent = `${formatNumber(metrics.max_drawdown_pct ?? 0, 2)}%`;
    }
  }

  function renderPaperEvents(payload) {
    const rows = payload.events || [];
    if (!elements.paperEventsBody || !elements.paperEventsEmpty) {
      return;
    }
    elements.paperEventsBody.innerHTML = "";
    if (!rows.length) {
      elements.paperEventsEmpty.classList.remove("hidden");
      return;
    }
    elements.paperEventsEmpty.classList.add("hidden");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${formatDateTime(row.timestamp)}</td>
        <td>${escapeHtml(row.event_type || "-")}</td>
        <td>${escapeHtml(row.symbol || "-")}</td>
        <td>${escapeHtml(row.trade_id || "-")}</td>
        <td>${escapeHtml(row.summary || "-")}</td>
        <td>${row.pnl_value === null || row.pnl_value === undefined ? "-" : formatNumber(row.pnl_value, 4)}</td>
      `;
      elements.paperEventsBody.appendChild(tr);
    });
  }

  function renderPaperPortfolio(payload) {
    const portfolio = payload.portfolio || {};
    if (elements.paper.cashBalance) {
      elements.paper.cashBalance.textContent = formatNumber(portfolio.cash_balance, 4);
    }
    elements.paper.cashBalanceDetail.textContent = formatNumber(portfolio.cash_balance, 4);
    elements.paper.equity.textContent = formatNumber(portfolio.equity, 4);
    if (elements.paper.realizedPnl) {
      elements.paper.realizedPnl.textContent = formatNumber(portfolio.realized_pnl, 4);
    }
    elements.paper.realizedPnlDetail.textContent = formatNumber(portfolio.realized_pnl, 4);
    if (elements.paper.unrealizedPnl) {
      elements.paper.unrealizedPnl.textContent = formatNumber(portfolio.unrealized_pnl, 4);
    }
    elements.paper.unrealizedPnlDetail.textContent = formatNumber(portfolio.unrealized_pnl, 4);
    elements.paper.winCount.textContent = formatInteger(portfolio.win_count ?? 0);
    elements.paper.lossCount.textContent = formatInteger(portfolio.loss_count ?? 0);
    if (elements.hero.equity) {
      elements.hero.equity.textContent = formatNumber(portfolio.equity, 2);
    }
  }

  function renderOverviewSignals(rows) {
    elements.overview.signalList.innerHTML = "";
    const shortlist = rows.slice(0, 10);
    if (!shortlist.length) {
      elements.overview.signalEmpty.classList.remove("hidden");
      return;
    }
    elements.overview.signalEmpty.classList.add("hidden");
    shortlist.forEach((row) => {
      const tone = row.final_selected === true
        ? "strong"
        : typeof row.mean_signal === "number" && row.mean_signal >= 0.7
          ? "watch"
          : "watch";
      const stageText = row.final_selected === true
        ? (state.language === "tr" ? "aktif aday" : "active candidate")
        : (row.reject_stage === "STEP3"
            ? (state.language === "tr" ? "Adim 3 veto" : "Step3 veto")
            : row.reject_stage === "STEP2"
              ? (state.language === "tr" ? "Adim 2 veto" : "Step2 veto")
              : (state.language === "tr" ? "incelemede" : "pending"));
      const step2Text = typeof row.step2_score === "number" ? formatNumber(row.step2_score, 2) : "-";
      const item = document.createElement("article");
      item.className = "signal-radar-item";
      item.innerHTML = `
        <div class="signal-radar-main">
          <strong>${escapeHtml(row.symbol || "-")}</strong>
          <span>${escapeHtml(msg("signalHorizon", { horizon: row.decision_horizon || "-" }))}</span>
        </div>
        <div class="signal-radar-metrics">
          <span class="signal-pill signal-pill--${tone}">${formatNumber(row.mean_signal, 2)}</span>
          <span class="signal-meta">${escapeHtml(msg("step2", { score: step2Text }))}</span>
          <span class="signal-meta">${escapeHtml(stageText)}</span>
        </div>
      `;
      elements.overview.signalList.appendChild(item);
    });
  }

  function renderOverviewActivity(payloads) {
    if (!elements.overview.activityList || !elements.overview.activityEmpty) {
      return;
    }
    const { systemPayload, enginePayload, paperStatusPayload, aiPayload, aggregatePayload } = payloads;
    const entries = [];
    entries.push({
      title: enginePayload.running ? msg("engineActive") : msg("engineWaiting"),
      detail: enginePayload.last_error
        ? msg("lastIssue", { error: enginePayload.last_error })
        : msg("latestScanCount", { count: formatInteger(enginePayload.latest_signal_count ?? 0) }),
    });

    if ((aggregatePayload.signals || []).length) {
      const lead = aggregatePayload.signals[0];
      entries.push({
        title: msg("topSignal", { symbol: lead.symbol || "-" }),
        detail: msg("topSignalDetail", {
          score: formatNumber(lead.mean_signal, 2),
          regime: lead.regime_status || msg("regimePending"),
        }),
      });
    }

    elements.overview.activityList.innerHTML = "";
    entries.forEach((entry) => {
      const item = document.createElement("div");
      item.className = "activity-item";
      item.innerHTML = `
        <div class="activity-dot"></div>
        <div class="activity-copy">
          <strong>${escapeHtml(entry.title)}</strong>
          <span>${escapeHtml(entry.detail)}</span>
        </div>
      `;
      elements.overview.activityList.appendChild(item);
    });
    elements.overview.activityEmpty.classList.toggle("hidden", entries.length > 0);
  }

  function applyRuntimeConfig(configPayload) {
    const cfg = configPayload.runtime_config || {};
    syncDecisionHorizonOptions(cfg.supported_decision_horizons, cfg.decision_horizon || "");
    renderSupportedHorizons(cfg.supported_decision_horizons);
    elements.config.engineEnabled.checked = Boolean(cfg.engine_enabled);
    elements.config.engineUniverseSize.value = cfg.engine_universe_size ?? "";
    elements.config.engineRefreshSeconds.value = cfg.engine_refresh_seconds ?? "";
    elements.config.engineIncludeStep2.checked = Boolean(cfg.engine_include_step2);
    elements.config.engineIncludeStep3.checked = Boolean(cfg.engine_include_step3);
    elements.config.engineIncludeAiSupport.checked = Boolean(cfg.engine_include_ai_support);
    elements.config.engineMaxSignals.value = cfg.engine_max_signals ?? "";
    syncStaticTimeframeOptions(elements.config.snapshotTimeframe, cfg.snapshot_timeframe || "");
    elements.config.snapshotIntervalMinutes.value = cfg.snapshot_interval_minutes ?? "";
    elements.config.hourlyWindow.value = cfg.hourly_aggregation_window ?? "";
    elements.config.hourlyMinSnapshots.value = cfg.hourly_min_snapshots ?? "";
    elements.config.aggregationThreshold.value = cfg.aggregation_bullish_threshold ?? "";
    elements.config.aggregationWeightTrend.value = cfg.aggregation_weight_trend ?? "";
    elements.config.aggregationWeightSlope.value = cfg.aggregation_weight_slope ?? "";
    elements.config.aggregationWeightRsi.value = cfg.aggregation_weight_rsi ?? "";
    elements.config.aggregationWeightMacd.value = cfg.aggregation_weight_macd ?? "";
    elements.config.aggregationWeightAdx.value = cfg.aggregation_weight_adx ?? "";
    elements.config.aggregationWeightVolume.value = cfg.aggregation_weight_volume ?? "";
    elements.config.aggregationWeightBreakout.value = cfg.aggregation_weight_breakout ?? "";
    elements.config.aggregationStabilityCap.value = cfg.aggregation_stability_stddev_cap ?? "";
    syncStaticTimeframeOptions(elements.config.technicalMainTimeframe, cfg.technical_main_timeframe || "");
    syncStaticTimeframeOptions(elements.config.technicalConfirmationTimeframe, cfg.technical_confirmation_timeframe || "");
    elements.config.technicalSecondaryConfirmation.checked = Boolean(cfg.technical_use_secondary_confirmation);
    elements.config.technicalPassThreshold.value = cfg.technical_pass_threshold ?? "";
    elements.config.technicalOhlcvLimit.value = cfg.technical_ohlcv_limit ?? "";
    elements.config.technicalMinOhlcvRows.value = cfg.technical_min_ohlcv_rows ?? "";
    elements.config.technicalMaFast.value = cfg.technical_ma_fast_period ?? "";
    elements.config.technicalMaSlow.value = cfg.technical_ma_slow_period ?? "";
    elements.config.technicalMaSlopeLookback.value = cfg.technical_ma_slope_lookback ?? "";
    elements.config.technicalMaSlopeMinPct.value = cfg.technical_ma_slope_min_pct ?? "";
    elements.config.technicalMaSlopeGoodPct.value = cfg.technical_ma_slope_good_pct ?? "";
    elements.config.technicalAdxPeriod.value = cfg.technical_adx_period ?? "";
    elements.config.technicalAdxMin.value = cfg.technical_adx_min ?? "";
    elements.config.technicalAdxStrong.value = cfg.technical_adx_strong ?? "";
    elements.config.technicalRsiPeriod.value = cfg.technical_rsi_period ?? "";
    elements.config.technicalRsiMin.value = cfg.technical_rsi_bullish_min ?? "";
    elements.config.technicalRsiMax.value = cfg.technical_rsi_bullish_max ?? "";
    elements.config.technicalRsiExtreme.value = cfg.technical_rsi_extreme ?? "";
    elements.config.technicalMacdFast.value = cfg.technical_macd_fast ?? "";
    elements.config.technicalMacdSlow.value = cfg.technical_macd_slow ?? "";
    elements.config.technicalMacdSignal.value = cfg.technical_macd_signal ?? "";
    elements.config.technicalStochPeriod.value = cfg.technical_stoch_period ?? "";
    elements.config.technicalStochBullishMin.value = cfg.technical_stoch_bullish_min ?? "";
    elements.config.technicalStochOverbought.value = cfg.technical_stoch_overbought ?? "";
    elements.config.technicalAtrPeriod.value = cfg.technical_atr_period ?? "";
    elements.config.technicalAtrPctMin.value = cfg.technical_atr_pct_min ?? "";
    elements.config.technicalAtrPctMax.value = cfg.technical_atr_pct_max ?? "";
    elements.config.technicalBbandsPeriod.value = cfg.technical_bbands_period ?? "";
    elements.config.technicalBbandsStddev.value = cfg.technical_bbands_stddev ?? "";
    elements.config.technicalBbWidthCompressionMax.value = cfg.technical_bb_width_compression_max ?? "";
    elements.config.technicalBbWidthExpansionMin.value = cfg.technical_bb_width_expansion_min ?? "";
    elements.config.technicalOverextendedAboveUpperPct.value = cfg.technical_overextended_above_upper_pct ?? "";
    elements.config.technicalVolumeMaPeriod.value = cfg.technical_volume_ma_period ?? "";
    elements.config.technicalVolumeRatioMin.value = cfg.technical_volume_ratio_min ?? "";
    elements.config.technicalVolumeRatioStrong.value = cfg.technical_volume_ratio_strong ?? "";
    elements.config.technicalBreakoutLookback.value = cfg.technical_breakout_lookback ?? "";
    elements.config.technicalBreakoutBuffer.value = cfg.technical_breakout_buffer_pct ?? "";
    elements.config.technicalPullbackTolerancePct.value = cfg.technical_pullback_tolerance_pct ?? "";
    elements.config.technicalMissingCriticalPenalty.value = cfg.technical_missing_critical_penalty ?? "";
    elements.config.technicalSecondaryConfirmationPenalty.value = cfg.technical_secondary_confirmation_penalty ?? "";
    elements.config.technicalOverextendedPenalty.value = cfg.technical_overextended_penalty ?? "";
    elements.config.technicalNoisyPenalty.value = cfg.technical_noisy_penalty ?? "";
    elements.config.technicalWeightTrend.value = cfg.technical_weight_trend ?? "";
    elements.config.technicalWeightMomentum.value = cfg.technical_weight_momentum ?? "";
    elements.config.technicalWeightVolatility.value = cfg.technical_weight_volatility ?? "";
    elements.config.technicalWeightVolume.value = cfg.technical_weight_volume ?? "";
    elements.config.technicalWeightEntry.value = cfg.technical_weight_entry ?? "";
    elements.config.technicalCriticalIndicators.value = (cfg.technical_critical_indicators || []).join(", ");
    elements.config.regimeBtcSymbol.value = cfg.regime_btc_symbol || "";
    syncStaticTimeframeOptions(elements.config.regimeTimeframe, cfg.regime_timeframe || "");
    elements.config.regimeOhlcvLimit.value = cfg.regime_ohlcv_limit ?? "";
    elements.config.regimeMinOhlcvRows.value = cfg.regime_min_ohlcv_rows ?? "";
    elements.config.regimeBtcMaFast.value = cfg.regime_btc_ma_fast_period ?? "";
    elements.config.regimeBtcMaSlow.value = cfg.regime_btc_ma_slow_period ?? "";
    elements.config.regimeBtcSlopeLookback.value = cfg.regime_btc_slope_lookback ?? "";
    elements.config.regimeBtcSlopeMinPct.value = cfg.regime_btc_slope_min_pct ?? "";
    elements.config.regimeBtcSlopeGoodPct.value = cfg.regime_btc_slope_good_pct ?? "";
    elements.config.regimeAdxPeriod.value = cfg.regime_adx_period ?? "";
    elements.config.regimeAdxMin.value = cfg.regime_adx_min ?? "";
    elements.config.regimeAdxStrong.value = cfg.regime_adx_strong ?? "";
    elements.config.regimeAtrPeriod.value = cfg.regime_atr_period ?? "";
    elements.config.regimeBreadthEnabled.checked = Boolean(cfg.regime_breadth_enabled);
    syncStaticTimeframeOptions(elements.config.regimeBreadthTimeframe, cfg.regime_breadth_timeframe || "");
    elements.config.regimeBreadthSymbolCount.value = cfg.regime_breadth_symbol_count ?? "";
    elements.config.regimeBreadthMinSamples.value = cfg.regime_breadth_min_samples ?? "";
    elements.config.regimeBreadthFastPeriod.value = cfg.regime_breadth_fast_period ?? "";
    elements.config.regimeBreadthSlowPeriod.value = cfg.regime_breadth_slow_period ?? "";
    elements.config.regimeBreadthBullishRatio.value = cfg.regime_breadth_bullish_ratio ?? "";
    elements.config.regimeBreadthBearishRatio.value = cfg.regime_breadth_bearish_ratio ?? "";
    elements.config.regimeDerivativesEnabled.checked = Boolean(cfg.regime_derivatives_enabled);
    elements.config.regimeDerivativesSymbol.value = cfg.regime_derivatives_symbol || "";
    elements.config.regimeFundingAbsMax.value = cfg.regime_funding_abs_max ?? "";
    elements.config.regimeDerivativesNeutralScore.value = cfg.regime_derivatives_neutral_score ?? "";
    elements.config.regimeFallbackPenaltyPoints.value = cfg.regime_fallback_penalty_points ?? "";
    elements.config.regimeAtrDanger.value = cfg.regime_atr_danger_pct ?? "";
    elements.config.regimeDrawdownLookback.value = cfg.regime_drawdown_lookback ?? "";
    elements.config.regimeDrawdownDanger.value = cfg.regime_drawdown_danger_pct ?? "";
    elements.config.regimeBullishThreshold.value = cfg.regime_score_bullish_threshold ?? "";
    elements.config.regimeNeutralThreshold.value = cfg.regime_score_neutral_threshold ?? "";
    elements.config.regimeAllowNeutral.checked = Boolean(cfg.regime_allow_neutral);
    elements.config.regimeVetoBearish.checked = Boolean(cfg.regime_veto_if_bearish);
    elements.config.regimeVetoDanger.checked = Boolean(cfg.regime_veto_if_danger);
    elements.config.regimeWeightTrend.value = cfg.regime_weight_trend ?? "";
    elements.config.regimeWeightVolatility.value = cfg.regime_weight_volatility ?? "";
    elements.config.regimeWeightBreadth.value = cfg.regime_weight_breadth ?? "";
    elements.config.regimeWeightDerivatives.value = cfg.regime_weight_derivatives ?? "";
    elements.config.deepseekEnabled.checked = Boolean(cfg.deepseek_enabled);
    elements.config.llmProvider.value = cfg.llm_provider || "disabled";
    elements.config.deepseekShortlistLimit.value = cfg.deepseek_shortlist_limit ?? "";
    elements.config.deepseekMinAggregateScore.value = cfg.deepseek_min_aggregate_score ?? "";
    elements.config.deepseekModel.value = cfg.deepseek_model || "";
    elements.config.deepseekTimeoutSeconds.value = cfg.deepseek_timeout_seconds ?? "";
    elements.config.geminiModel.value = cfg.gemini_model || "";
    elements.config.geminiTimeoutSeconds.value = cfg.gemini_timeout_seconds ?? "";
    elements.config.paperEnabled.checked = Boolean(cfg.paper_bot_enabled);
    elements.config.paperInitialCapital.value = cfg.paper_initial_capital ?? "";
    elements.config.paperMaxOpenPositions.value = cfg.paper_max_open_positions ?? "";
    elements.config.paperRiskPerTradePct.value = cfg.paper_risk_per_trade_pct ?? "";
    elements.config.paperMinSignalScore.value = cfg.paper_min_signal_score ?? "";
    elements.config.paperRequireFinalSelected.checked = Boolean(cfg.paper_require_final_selected);
    elements.config.paperRequireStep2Pass.checked = Boolean(cfg.paper_require_step2_pass);
    elements.config.paperRequireStep3Pass.checked = Boolean(cfg.paper_require_step3_pass);
    elements.config.paperRequireWindowComplete.checked = Boolean(cfg.paper_require_window_complete);
    elements.config.paperAtrStopMultiplier.value = cfg.paper_atr_stop_multiplier ?? "";
    elements.config.paperRiskRewardRatio.value = cfg.paper_risk_reward_ratio ?? "";
    elements.config.paperMaxHoldMinutes.value = cfg.paper_max_hold_minutes ?? "";
    elements.config.paperFeeBps.value = cfg.paper_fee_bps ?? "";
    elements.config.paperSlippageBps.value = cfg.paper_slippage_bps ?? "";
    elements.config.paperRefreshSeconds.value = cfg.paper_refresh_seconds ?? "";
    elements.config.paperSyncEngineBeforeRun.checked = Boolean(cfg.paper_sync_engine_before_run);
    renderParameterSummary(cfg);
    renderParameterDiagnostics(cfg);
  }

  function buildConfigPayload() {
    return {
      decision_horizon: elements.config.decisionHorizon.value.trim(),
      engine_enabled: elements.config.engineEnabled.checked,
      engine_universe_size: parseInt(elements.config.engineUniverseSize.value, 10),
      engine_refresh_seconds: parseInt(elements.config.engineRefreshSeconds.value, 10),
      engine_include_step2: elements.config.engineIncludeStep2.checked,
      engine_include_step3: elements.config.engineIncludeStep3.checked,
      engine_include_ai_support: elements.config.engineIncludeAiSupport.checked,
      engine_max_signals: parseInt(elements.config.engineMaxSignals.value, 10),
      snapshot_timeframe: elements.config.snapshotTimeframe.value.trim(),
      snapshot_interval_minutes: parseInt(elements.config.snapshotIntervalMinutes.value, 10),
      hourly_aggregation_window: parseInt(elements.config.hourlyWindow.value, 10),
      hourly_min_snapshots: parseInt(elements.config.hourlyMinSnapshots.value, 10),
      aggregation_bullish_threshold: parseFloat(elements.config.aggregationThreshold.value),
      aggregation_weight_trend: parseFloat(elements.config.aggregationWeightTrend.value),
      aggregation_weight_slope: parseFloat(elements.config.aggregationWeightSlope.value),
      aggregation_weight_rsi: parseFloat(elements.config.aggregationWeightRsi.value),
      aggregation_weight_macd: parseFloat(elements.config.aggregationWeightMacd.value),
      aggregation_weight_adx: parseFloat(elements.config.aggregationWeightAdx.value),
      aggregation_weight_volume: parseFloat(elements.config.aggregationWeightVolume.value),
      aggregation_weight_breakout: parseFloat(elements.config.aggregationWeightBreakout.value),
      aggregation_stability_stddev_cap: parseFloat(elements.config.aggregationStabilityCap.value),
      technical_main_timeframe: elements.config.technicalMainTimeframe.value.trim(),
      technical_confirmation_timeframe: elements.config.technicalConfirmationTimeframe.value.trim(),
      technical_use_secondary_confirmation: elements.config.technicalSecondaryConfirmation.checked,
      technical_pass_threshold: parseFloat(elements.config.technicalPassThreshold.value),
      technical_ohlcv_limit: parseInt(elements.config.technicalOhlcvLimit.value, 10),
      technical_min_ohlcv_rows: parseInt(elements.config.technicalMinOhlcvRows.value, 10),
      technical_ma_fast_period: parseInt(elements.config.technicalMaFast.value, 10),
      technical_ma_slow_period: parseInt(elements.config.technicalMaSlow.value, 10),
      technical_ma_slope_lookback: parseInt(elements.config.technicalMaSlopeLookback.value, 10),
      technical_ma_slope_min_pct: parseFloat(elements.config.technicalMaSlopeMinPct.value),
      technical_ma_slope_good_pct: parseFloat(elements.config.technicalMaSlopeGoodPct.value),
      technical_adx_period: parseInt(elements.config.technicalAdxPeriod.value, 10),
      technical_adx_min: parseFloat(elements.config.technicalAdxMin.value),
      technical_adx_strong: parseFloat(elements.config.technicalAdxStrong.value),
      technical_rsi_period: parseInt(elements.config.technicalRsiPeriod.value, 10),
      technical_rsi_bullish_min: parseFloat(elements.config.technicalRsiMin.value),
      technical_rsi_bullish_max: parseFloat(elements.config.technicalRsiMax.value),
      technical_rsi_extreme: parseFloat(elements.config.technicalRsiExtreme.value),
      technical_macd_fast: parseInt(elements.config.technicalMacdFast.value, 10),
      technical_macd_slow: parseInt(elements.config.technicalMacdSlow.value, 10),
      technical_macd_signal: parseInt(elements.config.technicalMacdSignal.value, 10),
      technical_stoch_period: parseInt(elements.config.technicalStochPeriod.value, 10),
      technical_stoch_bullish_min: parseFloat(elements.config.technicalStochBullishMin.value),
      technical_stoch_overbought: parseFloat(elements.config.technicalStochOverbought.value),
      technical_atr_period: parseInt(elements.config.technicalAtrPeriod.value, 10),
      technical_atr_pct_min: parseFloat(elements.config.technicalAtrPctMin.value),
      technical_atr_pct_max: parseFloat(elements.config.technicalAtrPctMax.value),
      technical_bbands_period: parseInt(elements.config.technicalBbandsPeriod.value, 10),
      technical_bbands_stddev: parseFloat(elements.config.technicalBbandsStddev.value),
      technical_bb_width_compression_max: parseFloat(elements.config.technicalBbWidthCompressionMax.value),
      technical_bb_width_expansion_min: parseFloat(elements.config.technicalBbWidthExpansionMin.value),
      technical_overextended_above_upper_pct: parseFloat(elements.config.technicalOverextendedAboveUpperPct.value),
      technical_volume_ma_period: parseInt(elements.config.technicalVolumeMaPeriod.value, 10),
      technical_volume_ratio_min: parseFloat(elements.config.technicalVolumeRatioMin.value),
      technical_volume_ratio_strong: parseFloat(elements.config.technicalVolumeRatioStrong.value),
      technical_breakout_lookback: parseInt(elements.config.technicalBreakoutLookback.value, 10),
      technical_breakout_buffer_pct: parseFloat(elements.config.technicalBreakoutBuffer.value),
      technical_pullback_tolerance_pct: parseFloat(elements.config.technicalPullbackTolerancePct.value),
      technical_missing_critical_penalty: parseFloat(elements.config.technicalMissingCriticalPenalty.value),
      technical_secondary_confirmation_penalty: parseFloat(elements.config.technicalSecondaryConfirmationPenalty.value),
      technical_overextended_penalty: parseFloat(elements.config.technicalOverextendedPenalty.value),
      technical_noisy_penalty: parseFloat(elements.config.technicalNoisyPenalty.value),
      technical_weight_trend: parseFloat(elements.config.technicalWeightTrend.value),
      technical_weight_momentum: parseFloat(elements.config.technicalWeightMomentum.value),
      technical_weight_volatility: parseFloat(elements.config.technicalWeightVolatility.value),
      technical_weight_volume: parseFloat(elements.config.technicalWeightVolume.value),
      technical_weight_entry: parseFloat(elements.config.technicalWeightEntry.value),
      technical_critical_indicators: elements.config.technicalCriticalIndicators.value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      regime_btc_symbol: elements.config.regimeBtcSymbol.value.trim(),
      regime_timeframe: elements.config.regimeTimeframe.value.trim(),
      regime_ohlcv_limit: parseInt(elements.config.regimeOhlcvLimit.value, 10),
      regime_min_ohlcv_rows: parseInt(elements.config.regimeMinOhlcvRows.value, 10),
      regime_btc_ma_fast_period: parseInt(elements.config.regimeBtcMaFast.value, 10),
      regime_btc_ma_slow_period: parseInt(elements.config.regimeBtcMaSlow.value, 10),
      regime_btc_slope_lookback: parseInt(elements.config.regimeBtcSlopeLookback.value, 10),
      regime_btc_slope_min_pct: parseFloat(elements.config.regimeBtcSlopeMinPct.value),
      regime_btc_slope_good_pct: parseFloat(elements.config.regimeBtcSlopeGoodPct.value),
      regime_adx_period: parseInt(elements.config.regimeAdxPeriod.value, 10),
      regime_adx_min: parseFloat(elements.config.regimeAdxMin.value),
      regime_adx_strong: parseFloat(elements.config.regimeAdxStrong.value),
      regime_atr_period: parseInt(elements.config.regimeAtrPeriod.value, 10),
      regime_breadth_enabled: elements.config.regimeBreadthEnabled.checked,
      regime_breadth_timeframe: elements.config.regimeBreadthTimeframe.value.trim(),
      regime_breadth_symbol_count: parseInt(elements.config.regimeBreadthSymbolCount.value, 10),
      regime_breadth_min_samples: parseInt(elements.config.regimeBreadthMinSamples.value, 10),
      regime_breadth_fast_period: parseInt(elements.config.regimeBreadthFastPeriod.value, 10),
      regime_breadth_slow_period: parseInt(elements.config.regimeBreadthSlowPeriod.value, 10),
      regime_breadth_bullish_ratio: parseFloat(elements.config.regimeBreadthBullishRatio.value),
      regime_breadth_bearish_ratio: parseFloat(elements.config.regimeBreadthBearishRatio.value),
      regime_derivatives_enabled: elements.config.regimeDerivativesEnabled.checked,
      regime_derivatives_symbol: elements.config.regimeDerivativesSymbol.value.trim(),
      regime_funding_abs_max: parseFloat(elements.config.regimeFundingAbsMax.value),
      regime_derivatives_neutral_score: parseFloat(elements.config.regimeDerivativesNeutralScore.value),
      regime_fallback_penalty_points: parseFloat(elements.config.regimeFallbackPenaltyPoints.value),
      regime_atr_danger_pct: parseFloat(elements.config.regimeAtrDanger.value),
      regime_drawdown_lookback: parseInt(elements.config.regimeDrawdownLookback.value, 10),
      regime_drawdown_danger_pct: parseFloat(elements.config.regimeDrawdownDanger.value),
      regime_score_bullish_threshold: parseFloat(elements.config.regimeBullishThreshold.value),
      regime_score_neutral_threshold: parseFloat(elements.config.regimeNeutralThreshold.value),
      regime_allow_neutral: elements.config.regimeAllowNeutral.checked,
      regime_veto_if_bearish: elements.config.regimeVetoBearish.checked,
      regime_veto_if_danger: elements.config.regimeVetoDanger.checked,
      regime_weight_trend: parseFloat(elements.config.regimeWeightTrend.value),
      regime_weight_volatility: parseFloat(elements.config.regimeWeightVolatility.value),
      regime_weight_breadth: parseFloat(elements.config.regimeWeightBreadth.value),
      regime_weight_derivatives: parseFloat(elements.config.regimeWeightDerivatives.value),
      deepseek_enabled: elements.config.deepseekEnabled.checked,
      llm_provider: elements.config.llmProvider.value,
      deepseek_shortlist_limit: parseInt(elements.config.deepseekShortlistLimit.value, 10),
      deepseek_min_aggregate_score: parseFloat(elements.config.deepseekMinAggregateScore.value),
      deepseek_model: elements.config.deepseekModel.value.trim(),
      deepseek_timeout_seconds: parseInt(elements.config.deepseekTimeoutSeconds.value, 10),
      gemini_model: elements.config.geminiModel.value.trim(),
      gemini_timeout_seconds: parseInt(elements.config.geminiTimeoutSeconds.value, 10),
      paper_bot_enabled: elements.config.paperEnabled.checked,
      paper_initial_capital: parseFloat(elements.config.paperInitialCapital.value),
      paper_max_open_positions: parseInt(elements.config.paperMaxOpenPositions.value, 10),
      paper_risk_per_trade_pct: parseFloat(elements.config.paperRiskPerTradePct.value),
      paper_min_signal_score: parseFloat(elements.config.paperMinSignalScore.value),
      paper_require_final_selected: elements.config.paperRequireFinalSelected.checked,
      paper_require_step2_pass: elements.config.paperRequireStep2Pass.checked,
      paper_require_step3_pass: elements.config.paperRequireStep3Pass.checked,
      paper_require_window_complete: elements.config.paperRequireWindowComplete.checked,
      paper_atr_stop_multiplier: parseFloat(elements.config.paperAtrStopMultiplier.value),
      paper_risk_reward_ratio: parseFloat(elements.config.paperRiskRewardRatio.value),
      paper_max_hold_minutes: parseInt(elements.config.paperMaxHoldMinutes.value, 10),
      paper_fee_bps: parseFloat(elements.config.paperFeeBps.value),
      paper_slippage_bps: parseFloat(elements.config.paperSlippageBps.value),
      paper_refresh_seconds: parseInt(elements.config.paperRefreshSeconds.value, 10),
      paper_sync_engine_before_run: elements.config.paperSyncEngineBeforeRun.checked,
    };
  }

  function renderAggregateSignals(payload) {
      const rows = payload.signals || [];
      elements.aggregateBody.innerHTML = "";
      renderOverviewSignals(rows);
    if (!rows.length) {
      elements.aggregateEmpty.classList.remove("hidden");
      return;
    }
    elements.aggregateEmpty.classList.add("hidden");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      const breakout = row.latest_breakout === true;
      const windowComplete = row.aggregate_flags && row.aggregate_flags.window_complete === true;
      const fallbackUsed = row.fallback_used === true;
      tr.innerHTML = `
        <td>${escapeHtml(row.symbol || "-")}</td>
        <td>${escapeHtml(row.decision_horizon || "-")}</td>
        <td>${formatNumber(row.mean_signal, 4)}</td>
        <td>${formatNumber(row.bullish_ratio, 4)}</td>
        <td>${formatNumber(row.stability_score, 4)}</td>
        <td>${renderBooleanBadge(breakout, msg("yes"), msg("no"))}</td>
        <td>${renderBooleanBadge(windowComplete, msg("complete"), msg("incomplete"))}</td>
          <td>${renderBooleanBadge(fallbackUsed, msg("yes"), msg("no"), "badge-warning", "badge-enabled")}</td>
          <td>${formatNumber(row.step2_score, 2)}</td>
          <td>${renderBooleanBadge(row.step2_pass, msg("yes"), msg("no"))}</td>
          <td>${escapeHtml(row.regime_status || "-")}</td>
          <td>${renderBooleanBadge(row.step3_pass, msg("yes"), msg("no"))}</td>
          <td>${renderFinalStatusBadge(row)}</td>
          <td title="${escapeHtml(row.reject_reason_summary || "-")}">${renderRejectStageBadge(row)}</td>
        `;
        elements.aggregateBody.appendChild(tr);
      });
    }

  function renderAiSignals(payload) {
    const rows = payload.ai_signals || [];
    elements.aiBody.innerHTML = "";
    if (!rows.length) {
      elements.aiEmpty.classList.remove("hidden");
      return;
    }
    elements.aiEmpty.classList.add("hidden");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${escapeHtml(row.symbol || "-")}</td>
        <td>${escapeHtml(row.provider || state.llmProvider || "-")}</td>
        <td>${formatNumber(row.support_score, 2)}</td>
        <td>${formatNumber(row.narrative_strength, 2)}</td>
        <td>${escapeHtml(row.risk_label || "-")}</td>
        <td>${renderBooleanBadge(row.fallback_used === true, msg("yes"), msg("no"), "badge-warning", "badge-enabled")}</td>
        <td>${escapeHtml(row.summary || "-")}</td>
      `;
      elements.aiBody.appendChild(tr);
    });
  }

  function renderPaperTrades(payload, targetBody, emptyState, closed = false) {
    const rows = payload.trades || [];
    targetBody.innerHTML = "";
    if (!rows.length) {
      emptyState.classList.remove("hidden");
      return;
    }
    emptyState.classList.add("hidden");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = closed
        ? `
          <td>${escapeHtml(row.trade_id || "-")}</td>
          <td>${escapeHtml(row.symbol || "-")}</td>
          <td>${formatNumber(row.entry_price, 4)}</td>
          <td>${formatNumber(row.exit_price, 4)}</td>
          <td>${formatNumber(row.pnl_pct, 4)}</td>
          <td>${formatNumber(row.pnl_value, 4)}</td>
          <td>${escapeHtml(row.reason_closed || "-")}</td>
          <td>${formatDateTime(row.opened_at)}</td>
          <td>${formatDateTime(row.closed_at)}</td>
        `
        : `
          <td>${escapeHtml(row.trade_id || "-")}</td>
          <td>${escapeHtml(row.symbol || "-")}</td>
          <td>${formatNumber(row.entry_price, 4)}</td>
          <td>${formatNumber(row.current_price, 4)}</td>
          <td>${formatNumber(row.quantity, 6)}</td>
          <td>${formatNumber(row.pnl_pct, 4)}</td>
          <td>${formatNumber(row.pnl_value, 4)}</td>
          <td>${formatNumber(row.stop_loss, 4)}</td>
          <td>${formatNumber(row.take_profit, 4)}</td>
          <td>${formatDateTime(row.opened_at)}</td>
        `;
      targetBody.appendChild(tr);
    });
  }

  function renderHistoricalSimulation(payload) {
    const result = payload && payload.result ? payload.result : null;
    if (!result) {
      if (elements.historical.empty) {
        elements.historical.empty.classList.remove("hidden");
      }
      if (elements.historicalEvaluationsBody) {
        elements.historicalEvaluationsBody.innerHTML = "";
      }
      if (elements.historicalEvaluationsEmpty) {
        elements.historicalEvaluationsEmpty.classList.remove("hidden");
      }
      [
        elements.historical.resultSymbol,
        elements.historical.range,
        elements.historical.finalEquity,
        elements.historical.returnPct,
        elements.historical.netProfit,
        elements.historical.maxDrawdown,
        elements.historical.winRate,
      ].forEach((node) => {
        if (node) {
          node.textContent = "-";
        }
      });
      [
        elements.historical.openedTrades,
        elements.historical.closedTrades,
        elements.historical.selectedSignals,
        elements.historical.evaluations,
        elements.historical.warningCount,
      ].forEach((node) => {
        if (node) {
          node.textContent = "0";
        }
      });
      return;
    }

    if (elements.historical.empty) {
      elements.historical.empty.classList.add("hidden");
    }
    if (elements.historical.resultSymbol) {
      elements.historical.resultSymbol.textContent = result.symbol || "-";
    }
    if (elements.historical.range) {
      elements.historical.range.textContent = `${formatDateTime(result.start_at)} -> ${formatDateTime(result.end_at)}`;
    }
    if (elements.historical.finalEquity) {
      elements.historical.finalEquity.textContent = formatNumber(result.final_equity, 4);
    }
    if (elements.historical.returnPct) {
      elements.historical.returnPct.textContent = `${formatNumber(result.total_return_pct, 2)}%`;
    }
    if (elements.historical.openedTrades) {
      elements.historical.openedTrades.textContent = formatInteger(result.opened_trade_count ?? 0);
    }
    if (elements.historical.closedTrades) {
      elements.historical.closedTrades.textContent = formatInteger(result.closed_trade_count ?? 0);
    }
    if (elements.historical.selectedSignals) {
      elements.historical.selectedSignals.textContent = formatInteger(result.selected_signal_count ?? 0);
    }
    if (elements.historical.evaluations) {
      elements.historical.evaluations.textContent = formatInteger(result.evaluation_count ?? 0);
    }
    if (elements.historical.warningCount) {
      elements.historical.warningCount.textContent = formatInteger((result.warnings || []).length);
    }
    if (elements.historical.netProfit) {
      elements.historical.netProfit.textContent = formatNumber(result.metrics?.net_profit_value ?? 0, 4);
    }
    if (elements.historical.maxDrawdown) {
      elements.historical.maxDrawdown.textContent = `${formatNumber(result.metrics?.max_drawdown_pct ?? 0, 2)}%`;
    }
    if (elements.historical.winRate) {
      elements.historical.winRate.textContent = `${formatNumber(result.metrics?.win_rate_pct ?? 0, 2)}%`;
    }

    const evaluations = Array.isArray(result.evaluations) ? result.evaluations.slice(-25).reverse() : [];
    if (!elements.historicalEvaluationsBody || !elements.historicalEvaluationsEmpty) {
      return;
    }
    elements.historicalEvaluationsBody.innerHTML = "";
    if (!evaluations.length) {
      elements.historicalEvaluationsEmpty.classList.remove("hidden");
      return;
    }
    elements.historicalEvaluationsEmpty.classList.add("hidden");
    evaluations.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${formatDateTime(row.timestamp)}</td>
        <td>${formatNumber(row.mean_signal, 4)}</td>
        <td>${formatNumber(row.step2_score, 2)}</td>
        <td>${renderBooleanBadge(row.step2_pass, msg("yes"), msg("no"))}</td>
        <td>${escapeHtml(row.regime_status || "-")}</td>
        <td>${renderBooleanBadge(row.step3_pass, msg("yes"), msg("no"))}</td>
        <td>${renderFinalStatusBadge(row)}</td>
        <td>${formatInteger(row.opened_trades ?? 0)}</td>
        <td>${formatInteger(row.closed_trades ?? 0)}</td>
      `;
      elements.historicalEvaluationsBody.appendChild(tr);
    });
  }

  function rerenderFromState() {
    if (!state.latestPayloads) {
      return;
    }
    renderSystemStatus(state.latestPayloads.statusPayload);
    renderEngineStatus(state.latestPayloads.enginePayload);
    renderPaperStatus(state.latestPayloads.paperStatusPayload);
    renderPaperPortfolio(state.latestPayloads.paperPortfolioPayload);
    renderPaperMetrics(state.latestPayloads.paperMetricsPayload);
    renderPaperTrades(state.latestPayloads.paperOpenTradesPayload, elements.openTradesBody, elements.openTradesEmpty, false);
    renderPaperTrades(state.latestPayloads.paperClosedTradesPayload, elements.closedTradesBody, elements.closedTradesEmpty, true);
    renderPaperEvents(state.latestPayloads.paperEventsPayload);
    renderHistoricalSimulation(state.latestPayloads.historicalPayload);
    applyRuntimeConfig(state.latestPayloads.configPayload);
    renderAggregateSignals(state.latestPayloads.aggregatePayload);
    renderAiSignals(state.latestPayloads.aiPayload);
    renderOverviewActivity({
      systemPayload: state.latestPayloads.statusPayload,
      enginePayload: state.latestPayloads.enginePayload,
      paperStatusPayload: state.latestPayloads.paperStatusPayload,
      aiPayload: state.latestPayloads.aiPayload,
      aggregatePayload: state.latestPayloads.aggregatePayload,
    });
    updateLastUpdatedLabel();
  }

  async function refreshAll(options = {}) {
    const silent = options.silent === true;
    if (!silent) {
      setBanner("refreshing", "info");
    }
    try {
      const [
        statusPayload,
        configPayload,
        aggregatePayload,
        aiPayload,
        enginePayload,
        paperStatusPayload,
        paperPortfolioPayload,
        paperMetricsPayload,
        paperOpenTradesPayload,
        paperClosedTradesPayload,
        paperEventsPayload,
        historicalPayload,
      ] = await Promise.all([
        fetchJson("/system/status"),
        fetchJson("/runtime-config"),
        fetchJson("/signals/latest"),
        fetchJson("/signals/ai-support/latest"),
        fetchJson("/engine/status"),
        fetchJson("/paper/status"),
        fetchJson("/paper/portfolio"),
        fetchJson("/paper/metrics"),
        fetchJson("/paper/trades/open"),
        fetchJson("/paper/trades/closed"),
        fetchJson("/paper/events?limit=25"),
        fetchJson("/paper/historical/latest"),
      ]);
      state.latestPayloads = {
        statusPayload,
        configPayload,
        aggregatePayload,
        aiPayload,
        enginePayload,
        paperStatusPayload,
        paperPortfolioPayload,
        paperMetricsPayload,
        paperOpenTradesPayload,
        paperClosedTradesPayload,
        paperEventsPayload,
        historicalPayload,
      };
      rerenderFromState();
      elements.runtimeError.classList.add("hidden");
      elements.runtimeError.textContent = "";
      state.lastUpdatedAt = new Date();
      updateLastUpdatedLabel();
      if (!silent) {
        setBanner("updated", "success");
      }
    } catch (error) {
      setBanner("refreshFailed", "error", { error: error.message });
    }
  }

  async function onConfigSubmit(event) {
    event.preventDefault();
    elements.runtimeError.classList.add("hidden");
    elements.runtimeError.textContent = "";
    try {
      await fetchJson("/runtime-config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildConfigPayload()),
      });
      setBanner("runtimeUpdated", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      elements.runtimeError.textContent = error.message;
      elements.runtimeError.classList.remove("hidden");
      setBanner("runtimeUpdateFailed", "error");
    }
  }

  async function onRuntimeReset() {
    try {
      await fetchJson("/runtime-config/reset", { method: "POST" });
      setBanner("runtimeReset", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("runtimeResetFailed", "error", { error: error.message });
    }
  }

  async function onEngineRunOnce() {
    setBanner("engineRunStarted", "info");
    try {
      await fetchJson("/engine/run-once", { method: "POST" });
      setBanner("engineRunCompleted", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("engineRunFailed", "error", { error: error.message });
      await refreshAll({ silent: true });
    }
  }

  async function onEngineStart() {
    try {
      await fetchJson("/engine/start", { method: "POST" });
      setBanner("engineStarted", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("engineStartFailed", "error", { error: error.message });
    }
  }

  async function onEngineStop() {
    try {
      await fetchJson("/engine/stop", { method: "POST" });
      setBanner("engineStopped", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("engineStopFailed", "error", { error: error.message });
    }
  }

  async function onPaperRunOnce() {
    try {
      await fetchJson("/paper/run-once", { method: "POST" });
      setBanner("paperRunCompleted", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("paperRunFailed", "error", { error: error.message });
      await refreshAll({ silent: true });
    }
  }

  async function onPaperStart() {
    try {
      await fetchJson("/paper/start", { method: "POST" });
      setBanner("paperStarted", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("paperStartFailed", "error", { error: error.message });
    }
  }

  async function onPaperStop() {
    try {
      await fetchJson("/paper/stop", { method: "POST" });
      setBanner("paperStopped", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("paperStopFailed", "error", { error: error.message });
    }
  }

  async function onPaperReset() {
    try {
      await fetchJson("/paper/reset", { method: "POST" });
      setBanner("paperReset", "success");
      await refreshAll({ silent: true });
    } catch (error) {
      setBanner("paperResetFailed", "error", { error: error.message });
    }
  }

  function initializeHistoricalFormDefaults() {
    if (!elements.historical.startAt || !elements.historical.endAt) {
      return;
    }
    const end = new Date();
    const start = new Date(end.getTime() - (24 * 60 * 60 * 1000));
    if (!elements.historical.endAt.value) {
      elements.historical.endAt.value = toDatetimeLocalValue(end);
    }
    if (!elements.historical.startAt.value) {
      elements.historical.startAt.value = toDatetimeLocalValue(start);
    }
  }

  async function onHistoricalRun() {
    if (elements.historicalFormError) {
      elements.historicalFormError.classList.add("hidden");
      elements.historicalFormError.textContent = "";
    }
    const symbol = elements.historical.symbol ? elements.historical.symbol.value.trim().toUpperCase() : "";
    const startAt = elements.historical.startAt ? elements.historical.startAt.value : "";
    const endAt = elements.historical.endAt ? elements.historical.endAt.value : "";
    const closeAtEnd = elements.historical.closeOpen ? elements.historical.closeOpen.checked : true;
    if (!symbol || !startAt || !endAt) {
      if (elements.historicalFormError) {
        elements.historicalFormError.textContent = msg("historicalMissingFields");
        elements.historicalFormError.classList.remove("hidden");
      }
      setBanner("historicalMissingFields", "error");
      return;
    }
    setBanner("historicalStarted", "info");
    try {
      await fetchJson("/paper/historical/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol,
          start_at: new Date(startAt).toISOString(),
          end_at: new Date(endAt).toISOString(),
          close_open_positions_at_end: closeAtEnd,
        }),
      });
      setBanner("historicalCompleted", "success");
      await refreshAll({ silent: true });
      activateTab("paper-tab");
    } catch (error) {
      if (elements.historicalFormError) {
        elements.historicalFormError.textContent = error.message;
        elements.historicalFormError.classList.remove("hidden");
      }
      setBanner("historicalFailed", "error", { error: error.message });
    }
  }

  function stopAutoRefresh() {
    if (state.refreshTimer) {
      window.clearInterval(state.refreshTimer);
      state.refreshTimer = null;
    }
  }

  function startAutoRefresh() {
    stopAutoRefresh();
    if (!state.refreshEnabled) {
      updateRefreshUi();
      return;
    }
    state.refreshTimer = window.setInterval(() => {
      refreshAll({ silent: true });
    }, REFRESH_INTERVAL_MS);
    updateRefreshUi();
  }

  function toggleAutoRefresh() {
    state.refreshEnabled = !state.refreshEnabled;
    if (state.refreshEnabled) {
      startAutoRefresh();
      setBanner("autoRefreshResumedBanner", "info");
      return;
    }
    stopAutoRefresh();
    updateRefreshUi();
    setBanner("autoRefreshPausedBanner", "info");
  }

  function bindEvents() {
    elements.tabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.dataset.tabTarget;
        if (targetId) {
          activateTab(targetId);
        }
      });
    });
    elements.parameterSectionButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.dataset.parameterSectionTarget;
        if (targetId) {
          activateParameterSection(targetId);
        }
      });
    });
    if (elements.refreshNowBtn) {
      elements.refreshNowBtn.addEventListener("click", () => refreshAll());
    }
    if (elements.toggleRefreshBtn) {
      elements.toggleRefreshBtn.addEventListener("click", toggleAutoRefresh);
    }
    if (elements.engineRunOnceBtn) {
      elements.engineRunOnceBtn.addEventListener("click", onEngineRunOnce);
    }
    if (elements.engineStartBtn) {
      elements.engineStartBtn.addEventListener("click", onEngineStart);
    }
    if (elements.engineStopBtn) {
      elements.engineStopBtn.addEventListener("click", onEngineStop);
    }
    if (elements.paperRunOnceBtn) {
      elements.paperRunOnceBtn.addEventListener("click", onPaperRunOnce);
    }
    if (elements.paperStartBtn) {
      elements.paperStartBtn.addEventListener("click", onPaperStart);
    }
    if (elements.paperStopBtn) {
      elements.paperStopBtn.addEventListener("click", onPaperStop);
    }
    if (elements.paperResetBtn) {
      elements.paperResetBtn.addEventListener("click", onPaperReset);
    }
    if (elements.historicalRunBtn) {
      elements.historicalRunBtn.addEventListener("click", onHistoricalRun);
    }
    if (elements.runtimeForm) {
      elements.runtimeForm.addEventListener("submit", onConfigSubmit);
      ["input", "change"].forEach((eventName) => {
        elements.runtimeForm.addEventListener(eventName, () => {
          const draft = buildDraftConfig();
          renderParameterSummary(draft);
          renderParameterDiagnostics(draft);
        });
      });
    }
    if (elements.runtimeResetBtn) {
      elements.runtimeResetBtn.addEventListener("click", onRuntimeReset);
    }
    if (elements.languageSelector) {
      elements.languageSelector.addEventListener("change", (event) => setLanguage(event.target.value));
    }
  }

  function init() {
    if (!elements.runtimeForm) {
      return;
    }
    initializeHistoricalFormDefaults();
    applyTranslations();
    activateTab("overview-tab");
    activateParameterSection("parameter-step1");
    bindEvents();
    renderParameterSummary(buildDraftConfig());
    renderParameterDiagnostics(buildDraftConfig());
    startAutoRefresh();
    refreshAll();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
