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

    // 动作组分类：区分「带动作文件(.motion3.json)的真实动作」与「纯表情/开关」组，
    // 避免随机动作播放到「表情#2 / 秋千#1 / 绳子开关#5」这类只会设置表情或开关的组。
    function inGroup(name) { return function (g) { return (new RegExp(name, 'i')).test(g); }; }
    function groupHasFile(g) { return (motions[g] || []).some(function (m) { return !!m.File; }); }

    var fileGroups = motionGroups.filter(groupHasFile);  // 有真实动作文件的组
    var start = motionGroups.filter(inGroup('^start$|开场|开始|初始化'));
    var idleNamed = motionGroups.filter(inGroup('idle|tick|待机'));
    var idle = idleNamed.length
      ? idleNamed
      : fileGroups.filter(function (g) { return start.indexOf(g) < 0; });
    var action = fileGroups.filter(function (g) {
      return idle.indexOf(g) < 0 && start.indexOf(g) < 0;
    });
    if (!action.length) action = fileGroups.slice();

    // 随机播一组动作；skipFirst 时跳过下标 0（Live2D 惯例：第 0 个常是「回正」复位）
    function pickMotion(groups, skipFirst) {
      if (!groups.length) return Promise.resolve();
      var g = groups[Math.floor(Math.random() * groups.length)];
      var size = groupSizes[g] || 0;
      if (!size) return Promise.resolve();
      var idx = (skipFirst && size > 1)
        ? 1 + Math.floor(Math.random() * (size - 1))
        : Math.floor(Math.random() * size);
      return model.motion(g, idx);
    }

    // 待机动作循环：随机播待机组动作
    var idleTimer = null;
    function scheduleIdle(delay) { clearTimeout(idleTimer); idleTimer = setTimeout(playIdle, delay); }
    async function playIdle() {
      try {
        await pickMotion(idle, false);
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
          return pickMotion([g], true);
        }
        return pickMotion(action, true);
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
