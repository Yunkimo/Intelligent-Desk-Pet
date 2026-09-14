/* 通用 Live2D 渲染（Cubism 4）：模型入口从 URL 参数读取，动作组/表情从模型元数据动态发现。 */
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

    // 模型入口（相对路径，如 cyrene/Cyrene.model3.json），默认昔涟
    var entry = (new URLSearchParams(location.search)).get('entry') || 'cyrene/Cyrene.model3.json';

    // 从模型元数据发现动作组（供待机/随机动作），避免硬编码某个模型的动作组名
    var motionGroups = [];
    var groupSizes = {};
    try {
      var meta = await (await fetch(entry)).json();
      var motions = (meta.FileReferences && meta.FileReferences.Motions) || {};
      motionGroups = Object.keys(motions);
      motionGroups.forEach(function (g) { groupSizes[g] = (motions[g] || []).length; });
    } catch (e) {
      window.__jsErrors.push('meta: ' + ((e && e.message) || e));
    }

    var model = await Live2DModel.from(entry);
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

    // 动作组分类：排除口型（对口型专用）与开场/初始化，避免随机动作播放到它们
    function inGroup(name) { return function (g) { return (new RegExp(name, 'i')).test(g); }; }
    var mouth = motionGroups.filter(inGroup('口型|口形|mouth|lip'));
    var start = motionGroups.filter(inGroup('^start$|开场|开始|初始化'));
    var idle = motionGroups.filter(inGroup('idle|tick|待机'));
    var action = motionGroups.filter(function (g) {
      return mouth.indexOf(g) < 0 && start.indexOf(g) < 0 && idle.indexOf(g) < 0;
    });
    if (!idle.length) {
      idle = motionGroups.filter(function (g) { return mouth.indexOf(g) < 0 && start.indexOf(g) < 0; });
    }
    if (!action.length) action = idle.slice();

    function pickMotion(groups) {
      if (!groups.length) return Promise.resolve();
      var g = groups[Math.floor(Math.random() * groups.length)];
      var size = groupSizes[g] || 0;
      if (!size) return Promise.resolve();
      return model.motion(g, Math.floor(Math.random() * size));
    }

    // 待机动作循环：随机播待机组动作
    var idleTimer = null;
    function scheduleIdle(delay) { clearTimeout(idleTimer); idleTimer = setTimeout(playIdle, delay); }
    async function playIdle() {
      try {
        await pickMotion(idle);
        scheduleIdle(2200);
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
      motion: function (g) {
        if (g && groupSizes[g]) {
          return model.motion(g, Math.floor(Math.random() * groupSizes[g]));
        }
        return pickMotion(action);
      },
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
