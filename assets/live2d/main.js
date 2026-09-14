/* 昔涟 Live2D：pixi-live2d-display (Cubism 4) 渲染，透明背景 + 待机动作循环。 */
window.__jsErrors = [];
window.addEventListener('error', function (e) {
  window.__jsErrors.push('error: ' + (e.message || e.type));
});
window.addEventListener('unhandledrejection', function (e) {
  var r = e.reason;
  window.__jsErrors.push('rejection: ' + ((r && r.message) || r));
});

(async function () {
  try {
    window.PIXI = PIXI; // 插件通过 window.PIXI.Ticker 自动驱动更新

    if (!PIXI || !PIXI.live2d) {
      throw new Error('PIXI.live2d 未加载 (typeof PIXI=' + typeof PIXI + ')');
    }

    var Live2DModel = PIXI.live2d.Live2DModel;
    Live2DModel.registerTicker(PIXI.Ticker);

    var app = new PIXI.Application({
      backgroundAlpha: 0, // 透明画布
      resizeTo: window,
      antialias: true,
      autoDensity: true,
      resolution: Math.max(1, window.devicePixelRatio || 1),
    });
    document.body.appendChild(app.view);

    var model = await Live2DModel.from('cyrene/Cyrene.model3.json');
    app.stage.addChild(model);
    model.autoInteract = true; // 眨眼 / 视线跟随 / 物理

    function layout() {
      var w = model.width || 1;
      var h = model.height || 1;
      var scale = Math.min(app.screen.width / w, app.screen.height / h) * 0.96;
      model.scale.set(scale);
      model.anchor.set(0.5, 0.5);
      model.x = app.screen.width / 2;
      model.y = app.screen.height * 0.52;
    }
    layout();
    window.addEventListener('resize', layout);

    // 待机动作循环（模型「Tick3」组：Wink/可爱/微笑/荡秋千 待机）
    var idleTimer = null;
    function scheduleIdle(delay) { clearTimeout(idleTimer); idleTimer = setTimeout(playIdle, delay); }
    async function playIdle() {
      try {
        await model.motion('Tick3', Math.floor(Math.random() * 4));
        scheduleIdle(2000);
      } catch (e) {
        scheduleIdle(3000);
      }
    }
    scheduleIdle(1200);

    window.__live2dReady = true;
    window.__live2dSize = { width: model.width, height: model.height };
    window.live2d = {
      model: model,
      layout: layout,
      motion: function (g, i) { return model.motion(g, i); },
      expression: function (n) { model.expression(n); },
    };
    window.__snapshot = function () {
      try {
        return app.renderer.extract.canvas(app.stage).toDataURL('image/png');
      } catch (e) {
        return 'ERROR:' + e;
      }
    };
  } catch (e) {
    window.__live2dReady = false;
    window.__live2dError = String((e && e.message) || e);
    window.__jsErrors.push('init: ' + window.__live2dError);
  }
})();
